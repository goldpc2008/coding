#! /usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
# import optparse

parser = argparse.ArgumentParser(description="Post Scan",usage='%(prog)s -H <target host> -p <target port>')
parser.add_argument('-H', dest='tgHost', type=str, help='specify target host')
parser.add_argument('-p', dest='tgPost', type=int, help='specify target post')

args = parser.parse_args()
print( args.tgHost,'\t',type(args.tgHost))
print( args.tgPost,'\t',type(args.tgPost))


