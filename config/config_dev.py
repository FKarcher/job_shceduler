#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'开发环境配置文件'
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

__author__ = 'Jadyn Liang'

# 数据库配置
DB_USERNAME = 'root'
DB_PASSWORD = '123456'
HOST = 'localhost'
DB_NAME = 'blog'
DB_URL_CONNECTION = 'mysql+pymysql://' + DB_USERNAME + ':' + DB_PASSWORD + '@' + HOST + '/' + DB_NAME + '?charset=utf8'
ENABLE_SQL_LOG = True

# 任务调度器配置
# If your workload involves CPU intensive operations,
# you should consider using ProcessPoolExecutor instead to make use of multiple CPU cores.
# You could even use both at once, adding the process pool executor as a secondary executor.
EXECUTORS = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(4)
}

# It is possible to set the maximum number of instances for a particular job that the scheduler will let run concurrently,
# by using the max_instances keyword argument when adding the job.
JOB_DEFAULTS = {
    'coalesce': False,
    'max_instances': 5
}

TIME_ZONE = 'utc'
