#! /usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import socket
# import optparse

# def connScan( tgHost, tgPort ):
#     try:
#         connSkt = socket.socket( socket.AF_INET,socket.SOCK_STREAM)
#         connSkt.connect((tgHost,tgPort))
#         print("[+]%d/tcp open" %tgPort )
#         connSkt.close()
#     except:
#         print("[+]%d/tcp close" %tgPort )

# def postScan( tgHost, tgPorts ):
#     try:
#         tgIP = socket.gethostbyname( tgHost )
#     except:
#         print("[-]Cannot resolve '%s': Unknown host" %tgHost )
#         return
#     try:
#         tgName =  socket.gethostbyaddr( tgIP )
#         print('\n[+]Scan Results for:'+tgName[0])
#     except:
#         print("\n[+]Scan Results for:"+tgIP )
    
#     socket.setdefaulttimeout(1)
    
#     for tgPort in tgPorts :
#         print( "Scanning port " + str(tgPort) )



parser = argparse.ArgumentParser(description="Post Scan",usage='%(prog)s -H <target host> -p <target port>')
parser.add_argument('-H', dest='tgHost', type=str, help='specify target host')
parser.add_argument('-p', dest='tgPort', type=str, help='specify target port (ex: 21,80,8080)')

args = parser.parse_args()

tgHost = args.tgHost
tgPort = args.tgPort

if ( tgHost == None) or ( tgPort == None ):
    print( "usage: args.py -H <target host> -p <target port>")
    exit( 0 )
else:
    tempPort = args.tgPort.split(',')
    print( args.tgHost )
    try:
        tgPort = [ int(p) for p in tempPort ]
        for p in tgPort :
            print( p, end='\t')
    except ValueError  as e :
        print( "Input Post Style Error :",e )    
    



