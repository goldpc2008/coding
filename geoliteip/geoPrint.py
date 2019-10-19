#! /usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import dpkt
import socket
import geoip2.database
import os

def printPcap( pcap):
    for ( ts , buf ) in pcap:
        try:
            eth = dpkt.ethernet.Ethernet( buf )
            ip = eth.data
            src = socket.inet_ntoa( ip.src )
            dst = socket.inet_ntoa( ip.dst )
            print('[*]Src:{0}--->{1}'.format( src , dst))
            srcInfo = getIPinformation( src )
            dstInfo = getIPinformation( dst )
            print('[+]Src Country:{0},City:{1}--->Dst:Country:{2},City:{3}\n'.format(srcInfo['country'],srcInfo['city'],dstInfo['country'],dstInfo['city'] ))

        except:
            pass

def getIPinformation(  ipAddress ):
    try:
        #判断GEOIP数据库是否存在当前目录下
        mmdbPath = os.path.join(os.getcwd(),'GeoLite2-City.mmdb')
        if os.path.isfile( mmdbPath) :
            pass
        else:
            print( "[*]The Path: {0} don't found GeoIp Database File.".format( mmdbPath))
            exit(0)
        rInfo = { }    
        reader  = geoip2.database.Reader( mmdbPath )
        response = reader.city( ipAddress )
        #获得IP地址相关的国家、省、市、邮编、经纬度
        try:
            continent = response.continent.names[ 'zh-CN']
        except Exception :
            continent = response.continent.name
        rInfo['continet'] = continent
        try:
            country = response.country.names['zh-CN']
        except Exception:
            country = response.country.name
        rInfo['country'] = country
        try:
            province = response.subdivisions.most_specific.names['zh-CN']
        except Exception :
            province = response.subdivisions.most_specific.name
        rInfo['province'] = province
        try:
            city =  response.city.names[ 'zh-CN']
        except Exception:
            city = response.city.name
        rInfo['city'] = city
        code = response.postal.code
        rInfo['code'] = code
        latitude = response.location.latitude
        rInfo['latitude'] = latitude
        longitude = response.location.longitude
        rInfo['longitude'] = longitude
        print('\n[*]Target: {0} GeoLiteDB-located:'.format(ipAddress))
        print('[+]Continent:{0}, Country:{1}, Province:{2}, City: {3}, Postcode:{4}'.format( continent,country,province,city,code))
        print('[+]Latitude: {}'.format( latitude ))
        print('[+]Longitude:{}'.format( longitude ))
        #关闭GeoLiteIp数据库
        reader.close()
        return rInfo
    except Exception as e :
        print("The IP Informat get Error: {}".format( e ))
        exit(0)



def main():
    #path = r'F:\pythoncode\coding\geoip'
    path = os.getcwd()
    pcapFile = os.path.join( path, 'geotest.pcap')
    if os.path.isfile ( pcapFile ) :
        with open( pcapFile, 'rb' ) as f :
            pcap = dpkt.pcap.Reader( f )
            printPcap( pcap )
    else:
        print( "[*]The File: {} no Found!!!".format( pcapFile))
    

if __name__ == "__main__":
    main()



