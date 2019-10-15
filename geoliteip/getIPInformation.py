#! /usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import geoip2.database
import os
import re

def getIPinformation(  ipAddress ):
    try:
        mmdbPath = os.path.join(os.getcwd(),'GeoLite2-City.mmdb')
        if os.path.isfile( mmdbPath) :
            pass
        else:
            print( "[*]The Path: {0} don't found GeoIp Database File.".format( mmdbPath))
            exit(0)
        
        reader  = geoip2.database.Reader( mmdbPath )
        response = reader.city( ipAddress )
        #获得IP地址相关的国家、省、市、邮编、经纬度
        continent = response.continent.names[ 'zh-CN']
        country = response.country.names['zh-CN']
        try:
            province = response.subdivisions.most_specific.names['zh-CN']
        except Exception :
            province = response.subdivisions.most_specific.name
        try:
            city =  response.city.names[ 'zh-CN']
        except Exception:
            city = response.city.name
        code = response.postal.code
        latitude = response.location.latitude
        longitude = response.location.longitude
        print('\n[*]Target: {0} GeoLiteDB-located:'.format(ipAddress))
        print('[+]Continent:{0}, Country:{1}, Province:{2}, City: {3}, Postcode:{4}'.format( continent,country,province,city,code))
        print('[+]Latitude: {}'.format( latitude ))
        print('[+]Longitude:{}'.format( longitude ))
        #关闭GeoLiteIp数据库
        reader.close()
    except Exception as e :
        print("The Porgrame runing error: {}".format( e ))

def checkIp( ip ):
    ll = ip.split( "." )
    for i in ll :
        si = int( i )
        if si<=0 or si>255 :
            return False
    return True

def main():
    # Main Program
    # getIPinformation( '58.247.88.22')
    # getIPinformation( '220.248.92.59')
    parser = argparse.ArgumentParser(description="Search IP Address Location City",usage='%(prog)s -I <target IP Address > ')
    parser.add_argument('-I', dest='tgIp', type=str, help='Ip Address Location City')
    
    args = parser.parse_args()

    tgIp = args.tgIp
    
    if ( tgIp == None ) :
        print( "usage: getIPinformation.py -I <target IP Address >  \n\t -I IP Address \n")
        exit( 0 )
    else:
        p =  re.compile( r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
        tl = p.findall( tgIp )
        if tl == None :
            print( "Not Found IP Address!!! ")
        else:
            llen = len( tl )
            for n in range( llen) :
                if checkIp( tl[n] ) :
                    getIPinformation( tl[n] )
                    # print( tl[n] )
                else:
                    print("\nThe IP Address: {0} Style Error!!! ".format( tl[n] ))


if __name__ == "__main__":
    main()


