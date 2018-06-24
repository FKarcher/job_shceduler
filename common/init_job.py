#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'定时任务初始化'
import importlib

from common.exception import ErrorCode, ServiceException
from service.job_service import JobService
from model.job import Job

__author__ = 'Jiateng Liang'
import os


def run():
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
            if not job:
                name = job_id
                # 动态导入脚本
                script = importlib.import_module('job.' + job_id)
                if hasattr(script, 'config'):
                    config = script.config
                    job = package_job(config, name, job_id)
                else:
                    job = Job(name=name, job_id=job_id)

                try:
                    JobService.insert_job(job)
                except Exception as e:
                    msg = '%s任务脚本导入失败' % job_id + '，详细信息：'
                    raise ServiceException(ErrorCode.FAIL, msg, str(e))


def package_job(config, default_name, default_job_id):
    job = Job()
    job.name = default_name if 'name' not in config else config['name']
    job.job_id = default_job_id if 'job_id' not in config else config['job_id']
    job.status = Job.Status.RUNNING.value if default_job_id == 'job_detect' else Job.Status.STOPPED.value
    job.cron = '' if 'cron' not in config else config['cron']
    job.type = 1 if 'type' not in config else config['type']
    job.start_date = '2000-01-01 00:00:00' if 'start_date' not in config else config['start_date']
    job.end_date = '2000-01-01 00:00:00' if 'end_date' not in config else config['end_date']
    job.instance_cnt = 1 if 'instance_cnt' not in config else config['instance_cnt']
    return job
