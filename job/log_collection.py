#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'日志回收...保留最近20天的日志，文件格式必须统一为xxx.log.2018-xx-xx'
__author__ = 'Jiateng Liang'

import os
from datetime import datetime, timedelta
from common.log import logger

PATH = '/root/repos/log/'
# PATH = '/Users/liangjiateng/Desktop/log/'


def run():
    logger.info('日志清理开始')
    cnt = 0
    if not os.path.exists(PATH):
        return
    dirs = os.listdir(PATH)
    for dir in dirs:
        dir = PATH + dir
        if os.path.isdir(dir):
            files = os.listdir(dir)
            for file_name in files:
                strs = file_name.split('.')
                if len(strs) == 3:
                    log_time = datetime.strptime(strs[2], '%Y-%m-%d').date()
                    now = datetime.now().date()
                    if now - timedelta(days=20) > log_time:
                        cnt += 1
                        os.remove(dir + '/' + file_name)
                        logger.info('日志：%s被清除' % (dir + '/' + file_name))

    logger.info('日志清理结束，清理了%s个日志' % cnt)


