#!/usr/bin/env python
# -*- coding:utf-8 -*-
import argparse
import zipfile
import os
import threading

n = 1
R = False

nprlock = threading.Semaphore( value= 1)
threadMaxlock=threading.BoundedSemaphore( value = 10 )

def extractFile( zFile, password):
    global n,R
    try:
        #传入的密码必须被转换为bytes类型，否则会出错
        zFile.extractall( path='./temp',pwd = bytes(password,encoding='utf-8'))
        print('[+]Password='+password+'\n') 
        R = True               
    except:
        nprlock.acquire()
        n += 1
        if (n % 100 == 0) :
            print("Passwrod has been passed : %d" %n)
    finally:
        nprlock.release()
    threadMaxlock.release()


def main():
    
    global n, R
    
    parser = argparse.ArgumentParser(description="Zip file crack" ,usage='%(prog)s -F <target zip file> -D <Password Dictionary file>')
    parser.add_argument('-F', dest='fzip', type=str, help='Want to crack zip file')
    parser.add_argument('-D', dest='fpd', type=str, help='Password Dictionary File')

    args = parser.parse_args()

    fzip = args.fzip
    fpd = args.fpd

    if ( fzip == None) or ( fpd == None ):
        print( "usage: unzip.py -F <target zip file> -D <Password Dictionary File> \n\t -F Target zip file \n\t -D Password Dictionary file \n")
        exit( 0 )
    if not os.path.exists( fzip) :
        print( "Missing required unzip files")
        exit(0)
    if not os.path.exists( fpd ) :
        print( "Missing required password dictionary files")
        exit(0)

    
    zFile = zipfile.ZipFile( fzip )
    with open( fpd ,'r',encoding='utf-8') as passFile :
        for line in passFile.readlines():
            if not R :
                password = line.strip('\n')
                threadMaxlock.acquire()
                t = threading.Thread(target=extractFile,args=( zFile, password))
                t.start()

    print( "Toutal pass password: %d" %n)

if __name__ == "__main__":
    main()

       
