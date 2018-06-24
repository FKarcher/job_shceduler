#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'自定义异常'
from datetime import datetime

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
        self.time = datetime.now()
        self.msg = msg
        self.detail = detail

    def get_log_msg(self):
        return '时间：' + self.time + '；错误码：' + self.error_code + '；错误信息：' + self.msg + '；详情：' + self.detail
