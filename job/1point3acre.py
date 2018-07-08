#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'一亩三分地自动登录服务'
__author__ = 'Jiateng Liang'
import requests
from bs4 import BeautifulSoup
import hashlib

headers = {'host': 'www.1point3acres.com',
           'origin': 'http://www.1point3acres.com',
           'referer': 'http://www.1point3acres.com/bbs/',
           'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/67.0.3396.87 Safari/537.36'}


def md5(word):
    return hashlib.md5(word.encode('utf-8')).hexdigest()


def login(username, password):
    password = md5(password)

    data = {'username': username, 'password': password, 'quickforward': 'yes', 'handlekey': 'ls'}

    res = requests.post(
        "http://www.1point3acres.com/bbs/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1",
        data=data, headers=headers)

    cookies = res.cookies

    sign_in(cookies)


def get_info(cookies):
    new_cookies = {'4Oaf_61d6_saltkey': cookies['4Oaf_61d6_saltkey'], '4Oaf_61d6_auth': cookies['4Oaf_61d6_auth']}
    print(new_cookies)
    info_res = requests.get('http://www.1point3acres.com/bbs/', headers=headers, cookies=new_cookies)
    # return_cookies = {'4Oaf_61d6_saltkey': info_res.cookies['4Oaf_61d6_saltkey'], '4Oaf_61d6_auth': info_res.cookies['4Oaf_61d6_auth']}

    print(info_res.text)


def sign_in(cookies):
    # new_cookies = {'4Oaf_61d6_saltkey': cookies['4Oaf_61d6_saltkey'],
    #                '4Oaf_61d6_auth': cookies['4Oaf_61d6_auth']}

    new_cookies = {'4Oaf_61d6_saltkey': 'TP81njpf',
                   '4Oaf_61d6_auth': '9d6c%2Bmsk2B%2FLr3c0QIEJ8fEEEtjM%2B9sOGgaKjqHLo7xTg9jbxM2%2FTQ5mwkH3PI%2BRhL87a85BGcAsike%2F%2BfyoNxjzEyM'}
    headers['referer'] = 'http://www.1point3acres.com/bbs/home.php?mod=spacecp&ac=credit&showcredit=1'

    data = {'formhash': '37b054a5', 'qdxq': 'kx', 'qdmode': 1, 'todaysay': 'im the best guy',
            'fastreply': 0}

    sign_in_res = requests.post(
        'http://www.1point3acres.com/bbs/plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=1&sign_as=1&inajax=1',
        data=data,
        headers=headers, cookies=new_cookies)
    print(sign_in_res.text)


login('602689817@qq.com', 'LJT5902879ZZ')
