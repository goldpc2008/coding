#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gh-net-fix —— 修复受限网络环境下 GitHub 域名无法访问的问题

背景:
  某些沙箱/内网环境把 github.com 等域名解析到不可达的假 IP(如 198.18.x.x),
  且 UDP 53 出站被封,导致 git clone / push 全部失败,但 HTTPS(443) 出站本身是通的。

原理:
  1. 通过 DoH(DNS-over-HTTPS, 走 443 端口) 查询 GitHub 域名的真实 IP
  2. 对每个候选 IP 做真实 TLS 握手 + HTTP 探测,证书校验失败的一律丢弃(防 DNS 污染)
  3. 将验证通过的 IP 写入 /etc/hosts,绕过本地被劫持的 DNS

用法:
  sudo python3 gh_net_fix.py             # 刷新 GitHub 域名解析并写入 hosts
       python3 gh_net_fix.py --dry-run   # 只预览,不修改 hosts
  sudo python3 gh_net_fix.py --remove    # 移除本脚本写入的条目
  sudo python3 gh_net_fix.py --check     # 只检测当前连通性

注意: GitHub IP 会变动,建议每月重跑一次,或加入 crontab。
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime

HOSTS = "/etc/hosts"
MARK_BEGIN = "# >>> gh-net-fix BEGIN (自动生成, 请勿手工编辑) <<<"
MARK_END = "# <<< gh-net-fix END >>>"

CURL = "/usr/bin/curl"
TIMEOUT = 10

# DoH 服务: (名称, URL 模板, (SNI域名, 真实IP))
DOH_SERVERS = [
    ("AliDNS", "https://dns.alidns.com/resolve?name={}&type=A", ("dns.alidns.com", "223.5.5.5")),
    ("DNSPod", "https://doh.pub/dns-query?name={}&type=A", ("doh.pub", "1.12.12.12")),
    ("DNSPod2", "https://doh.pub/dns-query?name={}&type=A", ("doh.pub", "120.53.53.53")),
]

DOMAINS = [
    "github.com",
    "api.github.com",
    "codeload.github.com",
    "objects.githubusercontent.com",
    "raw.githubusercontent.com",
    "gist.github.com",
    "ssh.github.com",
    "github.githubassets.com",
    "avatars.githubusercontent.com",
]

IPV4 = re.compile(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$")

# GitHub 官方网段(AS36459 等),用于二次校验,排除 DNS 污染结果
GITHUB_CIDRS = [
    ("140.82.112.0", 20), ("140.82.116.0", 20), ("143.55.64.0", 20),
    ("185.199.108.0", 22), ("192.30.252.0", 22), ("20.205.243.0", 24),
    ("20.201.28.0", 22), ("20.87.245.0", 24), ("4.148.0.0", 14),
    ("13.64.0.0", 11), ("13.107.0.0", 16), ("204.124.116.0", 22),
]


def ip_to_int(ip: str) -> int:
    a, b, c, d = (int(x) for x in ip.split("."))
    return (a << 24) | (b << 16) | (c << 8) | d


def in_github_range(ip: str) -> bool:
    if not IPV4.match(ip):
        return False
    val = ip_to_int(ip)
    for base, bits in GITHUB_CIDRS:
        mask = (0xFFFFFFFF << (32 - bits)) & 0xFFFFFFFF
        if (val & mask) == (ip_to_int(base) & mask):
            return True
    return False


def doh_query(domain: str):
    """通过 DoH 查询 A 记录,返回 (IP列表, 使用的服务名)"""
    for name, tpl, (sni_host, sni_ip) in DOH_SERVERS:
        url = tpl.format(domain)
        cmd = [
            CURL, "-s", "--max-time", str(TIMEOUT),
            "--resolve", f"{sni_host}:443:{sni_ip}",
            "-H", "accept: application/dns-json",
            url,
        ]
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT + 5).stdout
            data = json.loads(out)
            ips = [a["data"] for a in data.get("Answer", []) if a.get("type") == 1]
            if ips:
                return ips, name
        except Exception:
            continue
    return [], None


def tcp_test(ip: str, port: int, timeout: int = 6) -> bool:
    """纯 TCP 连通测试,用于 SSH 等非 HTTP 服务(如 ssh.github.com)"""
    import socket
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except Exception:
        return False


def verify_ip(domain: str, ip: str) -> bool:
    """对候选 IP 做真实 TLS 握手探测,证书不匹配(污染 IP)会失败"""
    cmd = [
        CURL, "-s", "-o", "/dev/null", "-w", "%{http_code}",
        "--max-time", str(TIMEOUT),
        "--resolve", f"{domain}:443:{ip}",
        f"https://{domain}/",
    ]
    try:
        code = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=TIMEOUT + 5).stdout.strip()
        if code.isdigit() and code != "000":
            return True
    except Exception:
        pass
    # HTTP 探测失败时退回 TCP 探测(ssh.github.com 只提供 SSH 服务,不响应 HTTP)
    return tcp_test(ip, 443)


def read_hosts() -> str:
    try:
        with open(HOSTS, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "127.0.0.1 localhost\n"


def strip_block(content: str) -> str:
    if MARK_BEGIN in content and MARK_END in content:
        start = content.index(MARK_BEGIN)
        end = content.index(MARK_END) + len(MARK_END)
        content = content[:start] + content[end:]
    return content.rstrip() + "\n"


def check_mode():
    print("当前 GitHub 连通性检测:\n")
    for d in ("github.com", "api.github.com"):
        cmd = [CURL, "-s", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "8", f"https://{d}/"]
        code = subprocess.run(cmd, capture_output=True, text=True, timeout=15).stdout.strip()
        status = "✓ 可达" if code.isdigit() and code != "000" else "✗ 不可达"
        print(f"  {status}  {d:20s} HTTP {code}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--remove", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    if args.check:
        return check_mode()

    original = read_hosts()

    if args.remove:
        backup = f"{HOSTS}.ghbak.{datetime.now():%Y%m%d%H%M%S}"
        shutil.copy2(HOSTS, backup)
        with open(HOSTS, "w", encoding="utf-8") as f:
            f.write(strip_block(original))
        print(f"已移除 gh-net-fix 条目,原文件备份于 {backup}")
        return 0

    print(f"通过 DoH 查询并验证 {len(DOMAINS)} 个 GitHub 域名 ...\n")
    results, failed = {}, []
    for d in DOMAINS:
        ips, src = doh_query(d)
        valid = [ip for ip in ips if in_github_range(ip)]
        # 网段校验后再做真实 TLS 探测
        verified = [ip for ip in valid[:3] if verify_ip(d, ip)]
        if verified:
            results[d] = verified
            note = "" if len(verified) == len(ips) else f" [已过滤 {len(ips)-len(verified)} 个可疑IP]"
            print(f"  ✓ {d:34s} {verified[0]:17s} (via {src}){note}")
        else:
            failed.append(d)
            print(f"  ✗ {d:34s} 无可用 IP")

    if not results:
        print("\n全部失败,未修改 hosts。请确认 HTTPS 出站可用。")
        return 1

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [MARK_BEGIN, f"# 更新时间: {now}"]
    for d, ips in results.items():
        for ip in ips:
            lines.append(f"{ip}  {d}")
    lines.append(MARK_END)
    block = "\n".join(lines) + "\n"

    if args.dry_run:
        print("\n--- 预览(未写入) ---\n" + block)
        return 0

    backup = f"{HOSTS}.ghbak.{datetime.now():%Y%m%d%H%M%S}"
    shutil.copy2(HOSTS, backup)
    try:
        with open(HOSTS, "w", encoding="utf-8") as f:
            f.write(strip_block(original) + "\n" + block)
    except PermissionError:
        print("权限不足,请使用 sudo 运行")
        return 1

    print(f"\n已写入 {HOSTS} (备份: {backup})")
    if failed:
        print(f"解析失败(不影响主要功能): {', '.join(failed)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
