#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'一亩三分地自动登录服务'
import re

__author__ = 'Jiateng Liang'
import requests
from bs4 import BeautifulSoup
import hashlib
from common.log import logger
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, BigInteger, DateTime
from sqlalchemy.ext.declarative import declarative_base
from common.enum import labels
from common.db import session, engine

BaseModel = declarative_base()


class AcreInfo(BaseModel):
    __tablename__ = "1point3acres_info"
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    username = Column(String(255), nullable=False, comment='用户名', unique=True)
    password = Column(String(255), nullable=False, comment='密码')
    real_name = Column(String(50), nullable=True, comment='真实用户名')
    point = Column(Integer, nullable=True, comment='积分')
    status = Column(Integer, nullable=False, default=1, comment='0不运行，1运行，-1删除')
    executed_times = Column(Integer, nullable=False, default=0, comment='签到次数')
    create_time = Column(DateTime, nullable=False)
    update_time = Column(DateTime, nullable=False, default=datetime.now())

    @labels
    class Status(Enum):
        """
        -1删除 0停止 1运行
        """
        DELETED = -1
        STOPPED = 0
        RUNNING = 1

        __labels__ = {
            DELETED: '已删除',
            STOPPED: '已停止',
            RUNNING: '运行中'
        }


headers = {'host': 'www.1point3acres.com',
           'origin': 'http://www.1point3acres.com',
           'referer': 'http://www.1point3acres.com/bbs/',
           'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/67.0.3396.87 Safari/537.36'}


def md5(word):
    return hashlib.md5(word.encode('utf-8')).hexdigest()


def login(username, password):
    """
    :param username:
    :param password: md5后的password
    :return:
    """

    data = {'username': username, 'password': password, 'quickforward': 'yes', 'handlekey': 'ls'}
    # cookies = {'4Oaf_61d6_saltkey': 'mPss7DJa'}
    resp = requests.post(
        "http://www.1point3acres.com/bbs/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1",
        data=data, headers=headers)
    # 去掉CDATA
    rgx = re.compile("\<\!\[CDATA\[(.*?)\]\]\>")
    m = rgx.search(resp.text)
    script_text = m.group(1)
    # 找获取token的url
    soup = BeautifulSoup(script_text, "lxml")
    urls = []
    for tag in soup.find_all('script'):
        urls.append(tag.get('src'))
    return resp.cookies['4Oaf_61d6_auth'], resp.cookies['4Oaf_61d6_saltkey'], urls


# def get_token(urls, auth, salt_key):
#     cookies = {'4Oaf_61d6_saltkey': auth, '4Oaf_61d6_auth': salt_key}
#     resp = requests.get(urls[1], headers=headers, cookies=cookies)
#     auth = resp.cookies['4Oaf_61d6_auth']
#     requests.get(urls[2], headers=headers, cookies=cookies)
#     requests.get(urls[3], headers=headers, cookies=cookies)
#     return auth


def get_info(auth, salt_key):
    """
    拉取信息接口
    :param auth:
    :param salt_key:
    :return: username, 积分, formhash
    """
    cookies = {'4Oaf_61d6_auth': auth, '4Oaf_61d6_saltkey': salt_key}
    info_res = requests.get('http://www.1point3acres.com/bbs/', headers=headers, cookies=cookies)
    soup = BeautifulSoup(info_res.text, "lxml")
    a_links = soup.find_all('a')
    formhash = None
    for link in a_links:
        if link.text == '退出':
            formhash = link.get('href').split('&')[2].split('=')[1]
    username = soup.find('strong', class_='vwmy').findChild('a').text
    point = soup.find('a', id='extcreditmenu').text.split(': ')[1]
    point = int(point)
    return username, point, formhash


def sign_in(auth, salt_key, formhash, username):
    """
    要验证的值：auth, salt_key, formhash
    :param auth:
    :param salt_key:
    :return:
    """
    cookies = {
        '4Oaf_61d6_auth': auth,
        '4Oaf_61d6_saltkey': salt_key}
    # cookies = {'4Oaf_61d6_auth': 'f3f9vOGrlxWBiWlfMC40Vm8jXTYxC5msoU3rV9Aqy1HJifTtTX8y8K2GNjJ5TjVXLqpXInniB2Ps8n6FgKHMj2FS1Mw', '4Oaf_61d6_saltkey': 'Ap3dz3P7'}

    headers['referer'] = 'http://www.1point3acres.com/bbs/home.php?mod=spacecp&ac=credit&showcredit=1'

    data = {'formhash': formhash, 'qdxq': 'kx', 'qdmode': 1, 'todaysay': 'im the best guy',
            'fastreply': 0}

    sign_in_res = requests.post(
        'http://www.1point3acres.com/bbs/plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=1&sign_as=1&inajax=1',
        data=data,
        headers=headers, cookies=cookies)

    res = re.search('恭喜你签到成功', sign_in_res.text)
    if res is not None:
        logger.info('用户%s今日签到成功！' % username)
        return True
    else:
        res = re.search('您今日已经签到', sign_in_res.text)
        if res is not None:
            logger.info('用户%s今日已经签到' % username)
        else:
            logger.info('用户%s签到异常' % username)
        return False


def get_user_by_username(username):
    acre_info = session.query(AcreInfo).filter(AcreInfo.username == username).first()
    if acre_info is None:
        raise Exception('一亩三分地用户%s不存在' % username)
    return acre_info


def list_users_by_status(status):
    return session.query(AcreInfo).filter(AcreInfo.status == status).all()


def update_user(username, real_name, point):
    acre_info = get_user_by_username(username)
    acre_info.real_name = real_name
    acre_info.point = point
    acre_info.executed_times += 1
    session.add(acre_info)
    session.commit()


def __run(login_username, password):
    try:
        login_auth, login_salt_key, urls = login(login_username, password)
    except Exception as e:
        logger.error('账号%s登录失败，可能是账号密码不正确，详情：%s' % (login_username, e))
        return
    try:
        username, point, hash = get_info(login_auth, login_salt_key)
    except Exception as e:
        logger.error('账号%s拉取信息失败，详情：%s' % (login_username, e))
        return
    try:
        sign_res = sign_in(login_auth, login_salt_key, hash, login_username)
    except Exception as e:
        logger.error('账号%s拉取信息失败，详情：%s' % (login_username, e))
        return
    update_user(login_username, username, point)


def run():
    """
    总入口
    :return:
    """
    try:
        logger.info('一亩三分地自动登录服务开始执行')
        for acre_info in list_users_by_status(AcreInfo.Status.RUNNING.value):
            __run(acre_info.username, acre_info.password)
        logger.info('一亩三分地自动登录服务结束执行')
    except Exception as ex:
        logger.error('未知异常：%s' % ex)
        session.rollback()
    finally:
        session.close()


run()
