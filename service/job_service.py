#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'job服务'
import importlib
import os
from datetime import datetime

from common.db import Session
from common.exception import ServiceException, ErrorCode, handle_exception
from model.job import Job

__author__ = 'Jiateng Liang'


class JobService(object):

    @staticmethod
    @handle_exception
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
    @handle_exception
    def get_job(job_id):
        """
        根据job_id获取job
        :param job_id:
        :return:
        """
        session = Session()
        job = session.query(Job).filter(Job.job_id == job_id).first()
        if job is None:
            raise ServiceException(ErrorCode.NOT_FOUND, '该任务不存在')
        return job

    @staticmethod
    @handle_exception
    def insert_job(job):
        if not job or not job.job_id or not job.name:
            raise ServiceException(ErrorCode.PARAM_ERROR, 'job参数错误，job_id或name不能为空')
        session = Session()
        if session.query(Job).filter(Job.job_id == job.job_id).first():
            raise ServiceException(ErrorCode.FAIL, 'job_id重复，该任务已经存在')
        job.create_time = datetime.now()
        session.add(job)
        session.commit()
        return job.job_id

    @staticmethod
    @handle_exception
    def add_executed_times(job_id, cnt):
        """
        增加任务运行次数
        :param job_id: job_id
        :param cnt: 次数
        :return:
        """
        session = Session()
        job = session.query(Job).filter(Job.job_id == job_id).first()
        if job is None:
            raise ServiceException(ErrorCode.NOT_FOUND, '该任务不存在')
        job.executed_times += cnt
        session.add(job)
        session.commit()
        return job.job_id

    @staticmethod
    @handle_exception
    def change_job_status(job_id, status):
        if status not in Job.Status.ALL:
            raise ServiceException(ErrorCode.PARAM_ERROR, 'status参数错误')
        session = Session()
        job = session.query(Job).filter(Job.job_id == job_id).first()
        if job is None:
            raise ServiceException(ErrorCode.NOT_FOUND, '该任务不存在')
        job.status = status.value
        session.add(job)
        session.commit()
        return job.job_id

    @staticmethod
    @handle_exception
    def load_jobs():
        """
        job导入脚本，执行后可将job目录下所有任务脚本导入到数据库
        :return:
        """
        # 列出job目录下所有文件, 文件名称作为job_id
        path = os.getcwd() + "/../job/"
        for filename in os.listdir(path):
            if filename != '__init__.py' and filename != '__pycache__':
                job_id = filename[:-3]
                job = JobService.get_job(job_id)
                # 存在则不插入
                if job is None:
                    name = job_id
                    # 动态导入脚本
                    script = importlib.import_module('job.' + job_id)
                    if hasattr(script, 'config'):
                        config = script.config
                        job = JobService.package_job(config, name, job_id)
                    else:
                        job = Job(name=name, job_id=job_id)

                    try:
                        JobService.insert_job(job)
                    except Exception as e:
                        msg = '%s任务脚本导入失败' % job_id + '，详细信息：'
                        raise ServiceException(ErrorCode.FAIL, msg, str(e))

    @staticmethod
    @handle_exception
    def package_job(config, default_name, default_job_id):
        job = Job()
        job.name = default_name if 'name' not in config else config['name']
        job.job_id = default_job_id if 'job_id' not in config else config['job_id']
        job.cron = '' if 'cron' not in config else config['cron']
        job.type = 1 if 'type' not in config else config['type']
        job.start_date = '2000-01-01 00:00:00' if 'start_date' not in config else config['start_date']
        job.end_date = '2000-01-01 00:00:00' if 'end_date' not in config else config['end_date']
        job.instance_cnt = 1 if 'instance_cnt' not in config else config['instance_cnt']
        return job

