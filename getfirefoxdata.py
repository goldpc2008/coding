#! /usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sqlite3
import re
import argparse

def printDownloads( downloadDB ):
    conn = sqlite3.connect( downloadDB )
    c = conn.cursor()
    c.execute( 'SELECT name, source, datetime( endTime/1000000,\'unixepoch\') FROM moz_downloads;')
    print('\n[*]-----File Downloads-----')
    for row in c :
        print( '[+]File {0} form source: {1} at: {2}'.format(str(row[0]),str(row[1]),str(row[2])))
    c.close()
    conn.close()

def printCookies( cookiesDB ):
    try:
        conn = sqlite3.connect( cookiesDB )
        c = conn.cursor()
        c.execute( 'SELECT host, name, value FROM moz_cookies;' )
        print('\n[*]-----Found Cookies-----')
        for row in c :
            host = row[0]
            name = row[1]
            value = row[2]
            print("[*]Host: {0}, Cookie: {1}, value: {2}".format(host,name,value))
        c.close()
        conn.close()
    except Exception as e :
        if 'encrypted' in str(e) :
            print("\n[*] Error reading your cookies database.")
            print("[*]Upgrade your Python-Sqlite3 Library")

def printHistory( placeDB ):
    try:
        conn = sqlite3.connect( placeDB)
        c = conn.cursor()
        c.execute("SELECT url, datetime( visit_date/1000000,'unixepoch') FROM moz_places, moz_historyvisits where visit_count >0 and moz_places.id ==moz_historyvisits.place_id;")
        print("\n[*]-----Found History-----")
        for row in c :
            url = row[0]
            date = row[1]
            if 'google' in str(url).lower() :
                r = re.findall( r'q=.*\&',url)
                if r :
                    search = r[0].split('&')[0]
                    search = search.replace('q=',"").replace('+'," ")
                    print('[+] {0}--Search For:{1}'.format( date, search))
            #print('[+] {0}--Visited: {1}'.format( date, url ))
        c.close()
        conn.close()
    except Exception as e:
        if 'encrypted' in str(e) :
            print("\n[*] Error reading your cookies database.")
            print("[*]Upgrade your Python-Sqlite3 Library")
        exit(0)


def main():
    parser = argparse.ArgumentParser(description="Show Firefox  Message",usage='%(prog)s -p <target Firefox File Path> ')
    parser.add_argument('-p', dest='tgPath', type=str, help='Firefox File Path')
    
    args = parser.parse_args()

    tgPath = args.tgPath
    
    if ( tgPath == None) :
        print( "usage: getfirefoxdata.py -p <target Firefox File Path>  \n\t -p Firefox File Path\n")
        exit( 0 )
    else:
        #path = os.path.join(tgPath,'firefox_profile') 
        dfname = os.path.join( tgPath,'downloads.sqlite')
        cfname = os.path.join( tgPath, 'cookies.sqlite' )
        hfname = os.path.join( tgPath, 'places.sqlite' )

        if os.path.isfile( dfname ):
            printDownloads( dfname )
        else:
            print( "The Path: {0}, Don't found Sqlite File: {1}".format( tgPath , dfname ))

        if os.path.isfile( cfname ):
            printCookies( cfname )
        else:
            print( "The Path: {0}, Don't found Sqlite File: {1}".format( tgPath , cfname ))
        
        if os.path.isfile( hfname ):
            printHistory( hfname )
        else:
            print( "The Path: {0}, Don't found Sqlite File: {1}".format( tgPath , hfname ))


if __name__ == "__main__":
    main()

