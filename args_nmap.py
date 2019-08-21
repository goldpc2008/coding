#! /usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import nmap

def nmapScan( tgHost, tgPort ):
    nmScan = nmap.PortScanner()
    results = nmScan.scan( tgHost, tgPort )
    state = results['scan'][tgHost]['tcp']
    for k in state :
        print("[*]"+tgHost+"tcp/"+str(k)+" "+state[k]['state'])

#主函数
def main() :
    parser = argparse.ArgumentParser(description="Post Scan",usage='%(prog)s -H <target host> -p <target port>')
    parser.add_argument('-H', dest='tgHost', type=str, help='specify target host')
    parser.add_argument('-p', dest='tgPort', type=str, help='specify target port (ex: 21,80,8080)')

    args = parser.parse_args()

    tgHost = args.tgHost
    tgPort = args.tgPort

    if ( tgHost == None) or ( tgPort == None ):
        print( "usage: args_nmap.py -H <target host> -p <target port> \n\t -H Host name\n\t -p Port no <ex:21,80,443,...> \n")
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

    nmapScan( tgHost, args.tgPort)  

if __name__ == "__main__":
    main()
