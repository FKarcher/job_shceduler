# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import re

'leetcode自动登录脚本，实现自动签到'
__author__ = 'Jiateng Liang'


def run(username, password):
    """
    运行函数
    :param username: 登录用户名
    :param password: 登录密码
    :return:
    """
    token, user_slag = login(username, password)
    get_info(token, user_slag)


def get_token(cookie):
    csrftoken = ''

    for msg in cookie.split(' '):
        if msg.startswith('csrftoken'):
            csrftoken = msg.split('=')[1].strip(';')
    return csrftoken


def login(username, password):
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
            'finished_contests': finished_contests, 'rating': rating, 'global_ranking': global_ranking,
            'solved_question': solved_question, 'accepted_submission': accepted_submission, 'points': points,
            'problems': problems, 'test_cases': test_cases}
    return info
