#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'执行入口'
from common.log import logger
from service.job_service import JobService
from thrift_server import server

__author__ = 'Jiateng Liang'

if __name__ == '__main__':
    # 防止意外停止
    JobService.stop_all_jobs()
    try:
        server.run()
    except Exception as ex:
        logger.error(ex)
