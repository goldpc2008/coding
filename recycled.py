#! /usr/bin/env python
# -*- coding:utf-8 -*-

import os
import winreg

def sid2user( sid ) :
    try:
        key =  winreg.open(winreg.HKEY_LOCAL_MACHINE,"OFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList"+"\\"+sid )
        (value,type) = winreg.QueryValueEx(key,'ProfileImagePath')
        user = value.split("\\")[-1]
        return user
    except:
        return sid

def returnDir ():
    dirs = [ r'c:\Recycler\ ', r'c:\Recycled\ ', r'c:\$Recycle.Bin\ ']
    for recycleDir in dirs :
        # print("{0}".format(recycleDir))
        if os.path.isdir( recycleDir ):
            return recycleDir.strip()
    return None

def findRecycled( recycleDir ):
    dirList = os.listdir( recycleDir )
    for sid in dirList :
        try:
            files = os.listdir( recycleDir+sid)
            user = sid2user( sid )
            print("\n[*] Listing Files for User: "+user)
            for file in files:
                print("[+] Found File: "+ file )
        except:
            print('\n[*] Open Directory:{0} Error'.format( recycleDir+sid))


def main():
    recycledDir = returnDir()
    if recycledDir :
        findRecycled( recycledDir)
        # print("The system Recycle Directory:{}".format(getinfo))
    else:
        print("No found system Recycle Directory")

if __name__ == "__main__":
    main()

