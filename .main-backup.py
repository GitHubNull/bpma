#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import argparse
from argparse import RawTextHelpFormatter
import time
import requests
import threading
from lxml import etree
from termcolor import *
import re



#parser = argparse.ArgumentParser(description='参数说明')
parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description='使用说明')
parser.add_argument('-ips', help='指定目标ip 目标域名 目标ip:端口 目标域名:端口记录文件')
parser.add_argument('-IPS', help='指定目标ip 目标域名 目标ip:端口 目标域名:端口记录文件')
parser.add_argument('-dirs', help='爆破路径的字典文件.(默认: config/dirs-lists/comment-dirs.txt)')
parser.add_argument('-users', help='指定爆破登录时所用的用户名字典文件(默认: config/users-list/comment-users.txt)')
parser.add_argument('-passwds', help='指定爆破登录时所使用的密码字典文件.(默认: config/passwds-lists/comment-passwds.txt)')
parser.add_argument('-proxy', help='指定代理地址，不使用代理请指定参数为n. (默认: http://127.0.0.1:8118)')
parser.add_argument('-success', help='指定爆破登录成功时出现的一些特殊字符字典文件.(默认: comment-success.txt)')
parser.add_argument('-failed', help='指定爆破登录时失败时出现的一些特征字符字典文件.(默认: comment-failed.txt)')
parser.add_argument('-out', help='指定爆破登录成功后将登录URL和对应的用户名以及密码保存到文件.(默认:default-res.txt)')
parser.add_argument('-surl', help='指定保存在phpMyAdmin后台登陆的URL的文件.(默认: success-urls.txt)')
parser.add_argument('-logfile', help='指定保存日志的文件，不使用日志文件而时输出到终端的指定参数为n.(默认: log.txt)')
parser.add_argument('-ca', help='指定是否输出最终执行时的参数.[y/Y, n/N] y或者Y输出，否则不输出. (默认: y)')
parser.add_argument('-statCode', help='指定成功返回登录界面的状态码参数. (默认: 200)')
parser.add_argument('-StatCode', help='指定成功返回登录界面时的状态码文件。 (默认: 无)')

args = parser.parse_args()

ips = ""
IPS = ''
dirs = "configs/dirs-lists/dir-list.txt"
users = "configs/users-lists/users-list.txt"
passwds = "configs/passwds-lists/top1001-password.txt"
proxy = "http://127.0.0.1:8118"
success = "configs/success-list/comment-success.txt"
failed = "configs/failed-lists/comment-failed.txt"
out = "default-res.txt"
surl = "success-urls.txt"
logfile = "logs/" + time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime()) + "-log.txt"
ca = 'y'
statCode = '200,301'
StatCode = ''

if args.ips is None and args.IPS is None:
    print "ips is must to be gave!"
    parser.print_help()
    sys.exit()
elif args.IPS is None and args.ips is not None:
    ips = args.ips
else:
    IPS = args.IPS

if args.dirs:
    dirs = args.dirs

if args.users:
    users =args.users

if args.passwds:
    passwds = args.passwds

if args.proxy:
    proxy = args.proxy

if args.success:
    success = args.success

if args.failed:
    failed = args.failed

if args.out:
    out = args.out

if args.surl:
    surl = args.surl

if args.logfile:
    logfile = args.logfile

if args.ca:
    ca = args.ca

if args.statCode:
    statCode = args.statCode

if args.StatCode:
    StatCode = args.StatCode

ipList = []
threads = []
dirList = []

def genIpList(ipSubStr):
    result = []
    if '/' in ipSubStr:
        tmp = ipSubStr.split('.')[0:3] + ipSubStr.split('.')[3].split('/') 
        if 24 == int(tmp[4]):
            for i in range(1, 255, 1):
                ip = tmp[0] + '.' + tmp[1] + '.' + tmp[2] + '.' + str(i)
                result.append(ip)
        elif 16 == int(tmp[4]):
            for i in range(0, 255, 1):
                for j in range(1, 255, 1):
                    ip = tmp[0] + '.' + tmp[1] + '.' + str(i) + '.' + str(j)
                    result.append(ip)
        elif 8 == int(tmp[4]):
            for i in range(0, 255, 1):
                for j in range(0, 255, 1):
                    for k in range(1, 255, 1):
                        ip = tmp[0] + '.' + str(i) + '.' + str(j) + '.' + str(k)
                        result.append(ip)
        else:
            return result

    elif '-' in ipSubStr:
        tmp = ipSubStr.split('.')[0:3] + ipSubStr.split('.')[3].split('-') 
        for i in range(int(tmp[3]), (int(tmp[4]) + 1), 1):
                ip = tmp[0] + '.' + tmp[1] + '.' + tmp[2] + '.' + str(i)
                result.append(ip)
    else:
        return result

    return result

if '' == ips and '' != IPS:
    ipList = genIpList(IPS)
else:
    print '----->L136'
    print 'ips:', ips
    print 'IPS:', IPS


for i in ipList:
    print i

