#!/usr/bin/env python
# -*- coding:utf-8 -*-

import zipfile

def extractFile( zFile, password):
    try:
        #传入的密码必须被转换为bytes类型，否则会出错
        zFile.extractall( path='./temp',pwd = bytes(password,encoding='utf-8'))
        return password
    except:
        return

def main():
    n = 1
    zFile = zipfile.ZipFile('./pytest.zip')
    with open('dpassword.txt','r',encoding='utf-8') as passFile :
        for line in passFile.readlines():
            password = line.strip('\n')
            # print( password )
            guess = extractFile(zFile,password)
            if guess:
                print('[+]Password='+password+'\n')
                print("Toutal pass password: %d " %n)
                exit(0)
            else:
                if (n % 100 == 0) :
                    print("Passwrod pass: %d" %n)
                n += 1 
    print( "Toutal pass password: %d" %n)

if __name__ == "__main__":
    main()

       
 
