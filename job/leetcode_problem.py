#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'leetcode题目抓取..'
import json
import requests

from common.db import session
from common.log import logger

from datetime import datetime
from enum import Enum

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

from common.enum import labels

__author__ = 'Jiateng Liang'

BaseModel = declarative_base()


class LeetcodeProblem(BaseModel):
    __tablename__ = "leetcode_problems"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    lid = Column(Integer, unique=True)
    title = Column(String(100), comment='题目')
    desc = Column(String, comment='题干')
    difficulty = Column(Integer, nullable=False, comment='1简单 2中等 3困难', default=0)
    is_locked = Column(Integer, nullable=False, comment='0没锁 1上锁', default=0)
    type = Column(Integer, default=0, comment='0算法，1数据库')
    submit_url = Column(String(255), comment='代码提交链接')
    code_def = Column(String, comment='代码初始化')
    create_time = Column(DateTime, nullable=False)
    update_time = Column(DateTime, nullable=False, default=datetime.now())

    @labels
    class Difficulty(Enum):
        """
        0简单 1中等 2困难
        """
        EASY = 0
        MEDIUM = 1
        HARD = 2

        __labels__ = {
            EASY: '简单',
            MEDIUM: '中等',
            HARD: '困难',
        }

    @labels
    class IsLocked(Enum):
        """
        0没锁 1上锁
        """
        UNLOCKED = 0
        LOCKED = 1

        __labels__ = {
            UNLOCKED: '解锁',
            LOCKED: '上锁',
        }

    @labels
    class Type(Enum):
        """
        0算法 1数据库
        """
        ALGO = 0
        DB = 1

        __labels__ = {
            ALGO: '算法',
            DB: '数据库',
        }


def __run(username, password):
    """
    运行函数
    :param username: 登录用户名
    :param password: 登录密码
    :return:
    """
    try:
        token, leetcode_session = login(username, password)
    except Exception as e:
        logger.warn('Username=%s登录异常，详情' % username, str(e))
        return
    if token is None:
        logger.warn('Username=%s登录失败' % username)
        return
    logger.info('========================开始爬取Leetcode题目信息=============================')
    process(token, leetcode_session)
    logger.info('========================Leetcode题目信息爬取完毕=============================')


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

    headers = {'authority': 'leetcode.com',
               'scheme': 'https',
               'origin': 'https://leetcode.com',
               'referer': 'https://leetcode.com/accounts/login/',
               'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/67.0.3396.87 Safari/537.36',
               'x-requested-with': 'XMLHttpRequest'}

    cookies = {'csrftoken': token}

    resp = requests.post("https://leetcode.com/accounts/login/", data=data, headers=headers, cookies=cookies)

    resp_cookies = resp.cookies

    return resp_cookies['csrftoken'], resp_cookies['LEETCODE_SESSION']


def process(token, leetcode_session):
    headers = {'referer': 'https://leetcode.com/',
               'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/67.0.3396.87 Safari/537.36'}

    cookies = {'csrftoken': token,
               'LEETCODE_SESSION': leetcode_session}

    res = requests.get("https://leetcode.com/api/problems/all/", headers=headers, cookies=cookies)

    json_map = json.loads(res.text)

    problems = json_map['stat_status_pairs']

    for p_info in problems:
        try:
            problem = LeetcodeProblem()
            problem.title = p_info['stat']['question__title']
            lid, desc, submit_url, code_def = get_detail(token, leetcode_session,
                                                         p_info['stat']['question__title_slug'])
            problem.lid = lid
            problem.desc = desc
            problem.submit_url = submit_url
            problem.code_def = code_def
            problem.difficulty = p_info['difficulty']['level']
            problem.type = LeetcodeProblem.Type.ALGO.value
            problem.is_locked = LeetcodeProblem.IsLocked.LOCKED.value if p_info[
                'paid_only'] else LeetcodeProblem.IsLocked.UNLOCKED.value
            save_into_db(problem)
            logger.info('算法题题号=%s，题目=%s信息爬取完毕' % (problem.lid, problem.title))
        except Exception as e:
            logger.error('算法题题号=%s，题目=%s信息爬取失败，详情：%s' % (problem.lid, problem.title, str(e)))
            session.rollback()

    res = requests.get("https://leetcode.com/api/problems/database/", headers=headers)

    json_map = json.loads(res.text)

    problems = json_map['stat_status_pairs']

    for p_info in problems:
        try:
            problem = LeetcodeProblem()
            problem.title = p_info['stat']['question__title']
            lid, desc, submit_url, code_def = get_detail(token, leetcode_session,
                                                         p_info['stat']['question__title_slug'])
            problem.lid = lid
            problem.desc = desc
            problem.submit_url = submit_url
            problem.code_def = code_def
            problem.difficulty = p_info['difficulty']['level']
            problem.type = LeetcodeProblem.Type.DB.value
            problem.is_locked = LeetcodeProblem.IsLocked.LOCKED.value if p_info[
                'paid_only'] else LeetcodeProblem.IsLocked.UNLOCKED.value
            save_into_db(problem)
            logger.info('DB题题号=%s，题目=%s信息爬取完毕' % (problem.lid, problem.title))
        except Exception as e:
            logger.error('DB题题号=%s，题目=%s信息爬取失败，详情：%s' % (problem.lid, problem.title, str(e)))
            session.rollback()


def get_detail(token, leetcode_session, title_slag):
    headers = {'referer': 'https://leetcode.com/problems/' + title_slag + '/description/',
               'origin': 'https://leetcode.com/',
               'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/67.0.3396.87 Safari/537.36',
               'x-csrftoken': token}

    cookies = {'csrftoken': token,
               'LEETCODE_SESSION': leetcode_session}

    data = {"operationName": "getQuestionDetail", "variables": {"titleSlug": title_slag},
            "query": "query getQuestionDetail($titleSlug: String!) {\n  isCurrentUserAuthenticated\n  question(titleSlug: $titleSlug) {\n    questionId\n    questionFrontendId\n    questionTitle\n    translatedTitle\n    questionTitleSlug\n    content\n    translatedContent\n    difficulty\n    stats\n    allowDiscuss\n    contributors\n    similarQuestions\n    mysqlSchemas\n    randomQuestionUrl\n    sessionId\n    categoryTitle\n    submitUrl\n    interpretUrl\n    codeDefinition\n    sampleTestCase\n    enableTestMode\n    metaData\n    enableRunCode\n    enableSubmit\n    judgerAvailable\n    infoVerified\n    envInfo\n    urlManager\n    article\n    questionDetailUrl\n    libraryUrl\n    companyTags {\n      name\n      slug\n      translatedName\n      __typename\n    }\n    companyTagStats\n    topicTags {\n      name\n      slug\n      translatedName\n      __typename\n    }\n    __typename\n  }\n  interviewed {\n    interviewedUrl\n    companies {\n      id\n      name\n      slug\n      __typename\n    }\n    timeOptions {\n      id\n      name\n      __typename\n    }\n    stageOptions {\n      id\n      name\n      __typename\n    }\n    __typename\n  }\n  subscribeUrl\n  isPremium\n  loginUrl\n}\n"}

    res = requests.post("https://leetcode.com/graphql", headers=headers, json=data, cookies=cookies)

    desc = None
    submit_url = None
    code_def = None
    lid = None
    json_map = json.loads(res.text)

    try:
        lid = json_map['data']['question']['questionFrontendId']
        desc = json_map['data']['question']['content']
        submit_url = json_map['data']['question']['submitUrl']
        code_def = json_map['data']['question']['codeDefinition']
    except Exception as e:
        logger.error('题目%s详情爬取失败，详情: %s' % title_slag, str(e))

    return lid, desc, submit_url, code_def


def save_into_db(problem):
    check = session.query(LeetcodeProblem).filter(LeetcodeProblem.lid == problem.lid).first()
    if check:
        check.lid = problem.lid
        check.title = problem.title
        check.desc = problem.desc
        check.difficulty = problem.difficulty
        check.is_locked = problem.is_locked
        check.type = problem.type
        check.submit_url = problem.submit_url
        check.code_def = problem.code_def
        check.update_time = datetime.now()
        session.add(check)
    else:
        problem.create_time = datetime.now()
        session.add(problem)
    session.commit()
