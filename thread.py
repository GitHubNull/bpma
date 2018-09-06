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

L = ['121.127.9.133', '121.127.9.134' '121.127.9.135', '121.127.9.136', '121.127.9.137']

def getPage(ip):
    url = 'http://' + ip + '/phpMyAdmin/'
    sys.stdout.write(url + '\n')
    try:
        resp = requests.get('http://' + ip + '/phpmyadmin', timeout=0.1)
        sys.stdout.write(str(resp.status_code) + '\n')
    except Exception, e:
        sys.stdout.write(str(e) + '\n')



for i in L:
    try:
        thread = threading.Thread(target = getPage, args=(i, ))
        thread.start()
    except Exception, e:
        sys.stdout.write(str(e) + '\n')


