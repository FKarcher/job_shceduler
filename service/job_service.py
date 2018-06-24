#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'job服务'
from datetime import datetime

from common.db import Session
from common.exception import ServiceException, ErrorCode
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
        if status is None:
            return session.query(Job).all()

        return session.query(Job).filter(Job.status == status).all()

    @staticmethod
    def get_job(job_id):
        """
        根据job_id获取job
        :param job_id:
        :return:
        """
        session = Session()
        return session.query(Job).filter(Job.job_id == job_id).first()

    @staticmethod
    def insert_job(job):
        if not job or not job.job_id or not job.name:
            raise ServiceException(ErrorCode.PARAM_ERROR, 'job参数错误，job_id或name不能为空')
        session = Session()
        if session.query(Job).filter(Job.job_id == job.job_id).first():
            raise ServiceException(ErrorCode.FAIL, 'job_id重复，该任务已经存在')
        job.create_time = datetime.now()
        session.add(job)
        session.commit()
