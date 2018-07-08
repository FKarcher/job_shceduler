# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, BigInteger, DateTime
from sqlalchemy.ext.declarative import declarative_base
from common.enum import labels
from common.db import session, engine
from common.log import logger
import base64

'leetcode自动登录脚本，实现自动签到'
__author__ = 'Jiateng Liang'

BaseModel = declarative_base()


class LeetcodeInfo(BaseModel):
    __tablename__ = "leetcode_info"
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    username = Column(String(255), nullable=False, comment='用户名', unique=True)
    user_slag = Column(String(255), nullable=True, comment='用户别名(用于url)')
    password = Column(String(255), nullable=False, comment='密码')
    real_name = Column(String(50), nullable=True, comment='姓名')
    avatar = Column(String(255), nullable=True, comment='头像url')
    location = Column(String(255), nullable=True, comment='地址')
    school = Column(String(50), nullable=True, comment='学校')
    finished_contests = Column(Integer, nullable=True, comment='完场比赛数')
    rating = Column(Integer, nullable=True, comment='排名')
    global_rank = Column(String(50), nullable=True, comment='总排名')
    solved_question = Column(String(50), nullable=True, comment='解决问题数')
    accepted_submission = Column(String(50), nullable=True, comment='解决问题数')
    points = Column(Integer, nullable=True, comment='金币数')
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


def run():
    leetcode_infos = list_leetcode_info_by_status(LeetcodeInfo.Status.RUNNING.value)
    for leetcode_info in leetcode_infos:
        password = base64.b64decode(leetcode_info.password).decode('utf-8')
        __run(leetcode_info.username, password)


def __run(username, password):
    """
    运行函数
    :param username: 登录用户名
    :param password: 登录密码
    :return:
    """
    try:
        token, user_slag = login(username, password)
        info = get_info(token, user_slag)
    except Exception as ex:
        logger.error('Username=%s账号leetcode爬取信息失败' % username)
        logger.error(ex)
        return

    info['username'] = username
    info['password'] = base64.b64encode(password.encode(encoding='utf-8'))
    try:
        update_info(info)
    except Exception as ex:
        logger.error(ex)
        session.rollback()
    logger.info('账号%s，Leetcode今日签到成功' % username)


def login(username, password):
    """
    登录leetcode
    :param username:
    :param password:
    :return:
    """

    def get_token(cookie):
        csrftoken = ''

        for msg in cookie.split(' '):
            if msg.startswith('csrftoken'):
                csrftoken = msg.split('=')[1].strip(';')
        return csrftoken

    # 获取token
    res = requests.get("https://leetcode.com")
    cookie = res.headers['Set-Cookie']

    token = get_token(cookie)

    data = {'login': username, 'password': password,
            'csrfmiddlewaretoken': token}

    headers = {'origin': 'https://leetcode.com',
               'referer': 'https://leetcode.com/accounts/login/',
               'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/67.0.3396.87 Safari/537.36',
               'cookie': '__cfduid=df5e01f1925b204689f6febcc69b11f9e1506110172; '
                         '__stripe_mid=5153ea41-e0e8-4636-8b13-6f985ef6ffb7; _ga=GA1.2.377648857.1510501634; '
                         '__atuvc=5%7C17%2C0%7C18%2C11%7C19%2C0%7C20%2C9%7C21; '
                         'csrftoken=' + token + '; '
                                                '_gid=GA1.2.1391822110.1529675267'}

    res = requests.post("https://leetcode.com/accounts/login/", data=data, headers=headers)

    soup = BeautifulSoup(res.text, "lxml")

    script_text = soup.find("script", text=re.compile(r"userSlug:(.+?),")).text

    user_slag = re.findall(r"userSlug:(.+?),", script_text)[0].strip().strip('\'')

    cookie = res.headers['Set-Cookie']

    return get_token(cookie), user_slag


def get_info(token, user_slag):
    """
    拉取信息
    :param token:
    :param user_slag:
    :return:
    """
    headers = {'referer': 'https://leetcode.com/',
               'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/67.0.3396.87 Safari/537.36',
               'cookie': '__cfduid=df5e01f1925b204689f6febcc69b11f9e1506110172; '
                         '__stripe_mid=5153ea41-e0e8-4636-8b13-6f985ef6ffb7; _ga=GA1.2.377648857.1510501634; '
                         '__atuvc=5%7C17%2C0%7C18%2C11%7C19%2C0%7C20%2C9%7C21; '
                         'csrftoken=' + token + '; '
                                                '_gid=GA1.2.1391822110.1529675267'}

    res = requests.get("https://leetcode.com/" + user_slag + "/", headers=headers)
    soup = BeautifulSoup(res.text, "lxml")
    # 获取信息
    avatar = soup.find("img", class_="img-rounded")['src']
    real_name = soup.find("h4", class_='realname').get_text().strip()
    username = soup.find("p", class_='username').get_text().strip()

    location_info = soup.find_all("span", class_='pull-right content-right-cut')

    location = location_info[0].get_text().strip()
    school = location_info[1].get_text().strip()

    problem_info = soup.find_all("span", class_="badge progress-bar-success")

    finished_contests = problem_info[0].get_text().strip()
    rating = problem_info[1].get_text().strip()
    global_ranking = problem_info[2].get_text().strip()
    solved_question = problem_info[3].get_text().strip()
    accepted_submission = problem_info[4].get_text().strip()
    points = problem_info[5].get_text().strip()
    problems = problem_info[6].get_text().strip()
    test_cases = problem_info[7].get_text().strip()

    info = {'avatar': avatar, 'real_name': real_name, 'username': username, 'location': location, 'school': school,
            'user_slag': user_slag,
            'finished_contests': finished_contests, 'rating': rating, 'global_ranking': global_ranking,
            'solved_question': solved_question, 'accepted_submission': accepted_submission, 'points': points,
            'problems': problems, 'test_cases': test_cases}
    return info


def update_info(info):
    """
    插入或更新信息
    :param info:
    :return:
    """
    username = info['username']
    leetcode_info = get_info_by_username(username)
    if leetcode_info is None:
        leetcode_info = LeetcodeInfo()
        leetcode_info.create_time = datetime.now()
    leetcode_info.username = info['username']
    leetcode_info.password = info['password']
    leetcode_info.user_slag = info['user_slag']
    leetcode_info.real_name = info['real_name']
    leetcode_info.avatar = info['avatar']
    leetcode_info.location = info['location']
    leetcode_info.school = info['school']
    leetcode_info.finished_contests = info['finished_contests']
    leetcode_info.rating = info['rating']
    leetcode_info.global_rank = info['global_ranking']
    leetcode_info.solved_question = info['solved_question']
    leetcode_info.accepted_submission = info['accepted_submission']
    leetcode_info.points = info['points']
    leetcode_info.executed_times += 1
    leetcode_info.status=LeetcodeInfo.Status.RUNNING.value
    session.add(leetcode_info)
    session.commit()


def get_info_by_username(username):
    """
    通过用户名获取用户信息
    :param username:
    :return:
    """
    return session.query(LeetcodeInfo).filter(LeetcodeInfo.username == username).first()


def list_leetcode_info_by_status(status):
    """
    列出信息
    :param status:
    :return:
    """
    return session.query(LeetcodeInfo).filter(LeetcodeInfo.status == status).all()



