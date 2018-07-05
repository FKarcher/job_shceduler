#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'测试环境配置文件'
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

__author__ = 'Jadyn Liang'

############ 数据库配置 #############
DB_USERNAME = 'test_liangjiateng'
DB_PASSWORD = 'liangjiateng'
HOST = 'localhost'
DB_NAME = 'blog_test'
DB_URL_CONNECTION = 'mysql+pymysql://' + DB_USERNAME + ':' + DB_PASSWORD + '@' + HOST + '/' + DB_NAME + '?charset=utf8'
ENABLE_SQL_LOG = False

########### 任务调度器配置 ###########
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
############# 时区设置 ############
TIME_ZONE = 'utc'

############# 日志配置 ############
LOG_NAME = 'Timed Task Test Mode'
LOG_CONSOLE = True  # 是否打印到控制台
LOG_LEVEL = 'INFO'  # DEBUG INFO WARN ERROR
LOG_PATH = '../log/job_scheduler/info.log'
LOG_FORMAT = '%(asctime)-15s %(levelname)s %(filename)s %(lineno)d %(process)d %(message)s'
LOG_DATE_FORMAT = "%a %d %b %Y %H:%M:%S"

############# RPC配置 ############
# 不要配成localhost!!!!
RPC_HOST = '127.0.0.1'
RPC_PORT = 9001