#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'任务探测脚本'

__author__ = 'Jiateng Liang'

config = {
    'name': '测试',
    'job_id': 'test',
    'cron': '{"seconds": 5}'
}


def run():
    print('测试任务脚本')
