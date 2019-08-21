#! /usr/bin/env python
#! -*- coding:utf-8 -*-

import argparse
import socket
import threading
# import optparse

#导入线程锁
screenLock = threading.Semaphore( value= 1)

#实现具体端口扫描(测试)功能
def connScan( tgHost, tgPort ):
    try:
        connSkt = socket.socket( socket.AF_INET,socket.SOCK_STREAM)
        connSkt.connect((tgHost,tgPort))
        connSkt.send(bytes('ViolentPython\r\n',encoding='utf-8'))
        results = connSkt.recv(100)
        screenLock.acquire()
        print("[+]%d/tcp open" %tgPort )
        print("[+]"+str(results,encoding='utf-8'))
        #connSkt.close()
    except:
        screenLock.acquire()
        print("[+]%d/tcp close" %tgPort )
    finally:
        screenLock.release()
        connSkt.close()


#根据输入的主机名(或IP地址)、端口列表，解析并开始扫描
def portScan( tgHost, tgPorts ):
    try:
        tgIP = socket.gethostbyname( tgHost )
    except:
        print("[-]Cannot resolve '%s': Unknown host" %tgHost )
        return
    try:
        tgName =  socket.gethostbyaddr( tgIP )
        print('\n[+]Scan Results for:'+tgName[0])
    except:
        print("\n[+]Scan Results for:"+tgIP )
    
    socket.setdefaulttimeout(1)
    
    for tgPort in tgPorts :
        print( "Scanning port " + str(tgPort) +">"*8)
        t = threading.Thread(target=connScan,args=(tgHost,tgPort))
        t.start()
        #connScan(tgHost,tgPort)

# portScan('www.baidu.com',[80,443,3389,1433,23,445])
#主函数
def main() :
    parser = argparse.ArgumentParser(description="Post Scan",usage='%(prog)s -H <target host> -p <target port>')
    parser.add_argument('-H', dest='tgHost', type=str, help='specify target host')
    parser.add_argument('-p', dest='tgPort', type=str, help='specify target port (ex: 21,80,8080)')

    args = parser.parse_args()

    tgHost = args.tgHost
    tgPort = args.tgPort

    if ( tgHost == None) or ( tgPort == None ):
        print( "usage: args.py -H <target host> -p <target port> \n\t -H Host name\n\t -p Port no <ex:21,80,443,...> \n")
        exit( 0 )
    else:
        tempPort = args.tgPort.strip().split(',')
        # print( args.tgHost )
        try:
            tgPort = [ int(p) for p in tempPort ]
            # for p in tgPort :
            #     print( p, end='\t')
            # print()
        except ValueError  as e :
            print( "Input Port Date Style Error >>>>>>>:",e ) 
            exit( 0 ) 

    portScan( tgHost, tgPort)  

if __name__ == "__main__":
    main()

    


