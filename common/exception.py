#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'自定义异常'
import functools
import json
import traceback
from datetime import datetime
from common.log import logger
from thrift_server.thrift_gen.ttypes import JobServiceException

__author__ = 'Jiateng Liang'


class ErrorCode(object):
    FAIL = -1
    INTERNAL_ERROR = 500
    SUCCESS = 200
    NOT_FOUND = 404
    PARAM_ERROR = 400


class ServiceException(Exception):

    def __init__(self, error_code, msg='', detail=''):
        Exception.__init__(self, msg)
        self.error_code = error_code
        self.time = str(datetime.now())
        self.msg = msg
        self.detail = detail

    def get_log_msg(self):
        return '时间：' + self.time + '；错误码：' + str(self.error_code) + '；错误信息：' + self.msg + '；详情：' + self.detail


# 异常捕捉器
def handle_exception(throwable):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            try:
                return func(*args, **kw)
            except Exception as e:
                if isinstance(e, ServiceException):
                    if e.error_code < 500:
                        logger.warn(e.get_log_msg())
                    else:
                        logger.error(e.get_log_msg())
                else:
                    exstr = traceback.format_exc()
                    logger.error(str(e) + '\n详情：' + exstr)

                if throwable:
                    job_exception = JobServiceException(e.error_code, e.msg, e.time, e.detail)
                    raise job_exception

        return wrapper

    return decorator
