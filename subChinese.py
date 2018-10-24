#!/usr/bin/env python
#encoding=utf-8
import sys
import os
import requests
import subprocess
from lxml import etree

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


def readFileLineByLine2Set(fileName):
    result = set()
    with open(fileName, 'r') as f:
        L = f.readline().strip()
        while L:
            result.add(L)
            L = f.readline().strip()
        f.close()

    return result

def getTarget(fileName):
    return readFileLineByLine2Set(fileName)

def getIpsAddressFromNet(target):
    result = ''
    ip = target.split(':')[0]
    if isIp(ip):
        req = 'http://www.ip138.com/ips1388.asp?ip=' + ip + '&action=2'
        resp = ''
        try:
            resp = requests.get(req)
        except Exception, e:
            sys.stdout.write(str(e) + '\n')
            return result
            
        html = etree.HTML(resp.content)
        lines = html.xpath('//li')
        if 1 < len(lines):
            tmp = lines[0].text.encode('utf-8')
            tmp2 = tmp.split('：')
            if 2 <= len(tmp2):
                result = tmp2[1]

    return result

def getCitys():
    return readFileLineByLine2Set('/opt/share/city.txt')

def getProvince():
    return readFileLineByLine2Set('/opt/share/province.txt')

def getArea():
    return readFileLineByLine2Set('/opt/share/area.txt')

def isChineseNet(srcTarget, ChineseCitys):
    addr = getIpsAddressFromNet(srcTarget)
    if '' == addr:
        return False
    for i in ChineseCitys:
        if i in  addr:
            return True

    return False

def subChineseAddress(targetList, ChineseCitys):
    #result = []
    for i in targetList:
        if not isChineseNet(i, ChineseCitys):     
            #result.append(i)
            print i
    #return result

targetList = list(getTarget(sys.argv[1]))
ChineseCitys = list(getCitys() | getProvince() | getArea())
ChineseCitys.append('中国')

#result = subChineseAddress(targetList, ChineseCitys)
subChineseAddress(targetList, ChineseCitys)

