#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'job服务'
from common.db import Session
from model.job import Job

__author__ = 'Jiateng Liang'


class JobService(object):

    @staticmethod
    def list_jobs_by_status(status=None):
        """
        列出所有Job
        :param status: -1删除 0停止 1执行 2暂停 3待加入
        :return: [Job]
        """
        session = Session()
        if not status:
            return session.query().all()

        return session.query(Job.status == status).all()
