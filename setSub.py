#!/usr/bin/env python
#encoding=utf-8
import sys
import os
import requests
import subprocess

if 3 != len(sys.argv):
    print "arg less 3!"
    sys.exit()



def isIp(Str):
    tmp = Str.split('.')
    if 4 != len(tmp):
        return False
    for i in tmp:
        if False == i.isdigit():
            return False
    return True

with open(sys.argv[1], 'r') as f1, open(sys.argv[2], 'r') as f2:

    line1 = f1.readline().strip()
        
    while line1:
        f2.seek(0, 0)
        line2 = f2.readline().strip()
        while line2:
            if line2 in line1:
                print line1
            line2 = f2.readline().strip()
            
        line1 = f1.readline().strip()

    f1.close()
    f2.close()
