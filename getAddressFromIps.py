#!/usr/bin/env python
#encoding=utf-8
import sys
import os
import requests
import subprocess

if 2 != len(sys.argv):
    print "arg less 2!"
    sys.exit()



def isIp(Str):
    tmp = Str.split('.')
    if 4 != len(tmp):
        return False
    for i in tmp:
        if False == i.isdigit():
            return False
    return True

with open(sys.argv[1], 'r') as f1:

    line1 = f1.readline().strip()
        
    while line1:
        ip = ''
        if 'http://' in line1 or 'https://' in line1:
            ip = line1.split('/')[2]
            if ':' in ip:
                ip = ip.split(':')[0]
        else:
            ip = line1
            if ':' in ip:
                ip = ip.split(':')[0]

        if isIp(ip):
            cmd = 'curl https://ip.cn/index.php?ip=' + ip
            #result = 
            #requests.get(url=cmd)
            os.system(cmd)
            #print result.content
        line1 = f1.readline().strip()

    f1.close()
