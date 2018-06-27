#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'job服务'
import importlib
import os
from datetime import datetime

from sqlalchemy import or_

from common.db import Session
from common.exception import ServiceException, ErrorCode, handle_exception
from model.job import Job
from common.scheduler import scheduler, RUNNING, STOPPED, PAUSED

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
        """
        改变任务状态
        :param job_id:
        :param status:
        :return:
        """
        all_status = [Job.Status.DELETED, Job.Status.STOPPED, Job.Status.RUNNING, Job.Status.SUSPENDED]
        if status not in all_status:
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


class JobRPCService(object):

    @staticmethod
    @handle_exception
    def start_scheduler():
        """
        启动调度器
        :return:
        """
        scheduler.start()

    @staticmethod
    @handle_exception
    def stop_scheduler():
        """
        停止调度器
        :return:
        """
        session = Session()
        jobs = session.query(Job).filter(
            or_(Job.status == Job.Status.RUNNING.value, Job.status == Job.Status.SUSPENDED.value)).all()
        for job in jobs:
            job.status = Job.Status.STOPPED.value
            session.add(job)
        session.commit()
        scheduler.shutdown()

    @staticmethod
    @handle_exception
    def pause_scheduler():
        """
        暂停调度器
        :return:
        """
        session = Session()
        jobs = session.query(Job).filter(Job.status == Job.Status.RUNNING.value).all()
        for job in jobs:
            job.status = Job.Status.SUSPENDED.value
            session.add(job)
        session.commit()
        scheduler.pause()

    @staticmethod
    @handle_exception
    def resume_scheduler():
        """
        重启调度器
        :return:
        """
        session = Session()
        jobs = session.query(Job).filter(Job.status == Job.Status.SUSPENDED.value).all()
        for job in jobs:
            job.status = Job.Status.RUNNING.value
            session.add(job)
        session.commit()
        scheduler.resume()

    @staticmethod
    @handle_exception
    def start_job(job_id):
        """
        开启一个停止的任务或者暂停的任务
        :param job_id:
        :return:
        """
        if scheduler.status() != RUNNING:
            raise ServiceException(ErrorCode.FAIL, '无法启动任务，调度器没有运行')
        session = Session()
        job = session.query(Job).filter(Job.job_id == job_id).first()
        if job is None:
            raise ServiceException(ErrorCode.NOT_FOUND, '该任务不存在')
        if job.status != Job.Status.STOPPED.value and job.status != Job.Status.SUSPENDED.value:
            raise ServiceException(ErrorCode.FAIL, '该任务无法启动，当前任务状态：%s' % job.Status.label(job.status))
        if job.status == Job.Status.STOPPED.value:
            scheduler.add_job(job)
        else:
            scheduler.resume_job(job)
        job.status = Job.Status.RUNNING.value
        session.add(job)
        session.commit()

    @staticmethod
    @handle_exception
    def stop_job(job_id):
        """
        任务停止
        :param job_id:
        :return:
        """
        session = Session()
        job = session.query(Job).filter(Job.job_id == job_id).first()
        if job is None:
            raise ServiceException(ErrorCode.NOT_FOUND, '该任务不存在')
        if job.status == Job.Status.STOPPED.value:
            raise ServiceException(ErrorCode.FAIL, '该任务已经停止')
        job.status = Job.Status.STOPPED.value
        session.add(job)
        session.commit()
        scheduler.remove_job(job)

    @staticmethod
    @handle_exception
    def modify_job(job_id, config):
        """
        修改任务规则
        :param job_id:
        :return:
        """
        session = Session()
        job = session.query(Job).filter(Job.job_id == job_id).first()
        if job is None:
            raise ServiceException(ErrorCode.NOT_FOUND, '该任务不存在')
        if job.status != Job.Status.STOPPED.value:
            raise ServiceException(ErrorCode.FAIL, '请先停止任务，当前状态：' + job.Status.label(job.status))
        try:
            job.name = config['name'] if 'name' in config else job.name
            job.cron = config['cron'] if 'cron' in config else job.cron
            job.type = config['type'] if 'type' in config else job.type
            job.instance_cnt = config['instance_cnt'] if 'instance_cnt' in config else job.instance_cnt
        except Exception as e:
            raise ServiceException(ErrorCode.PARAM_ERROR.value, '配置信息不正确')
        session.add(job)
        session.commit()


    @staticmethod
    @handle_exception
    def pause_job(job_id):
        """
        暂停任务
        :param job_id:
        :return:
        """
        session = Session()
        job = session.query(Job).filter(Job.job_id == job_id).first()
        if job is None:
            raise ServiceException(ErrorCode.NOT_FOUND, '该任务不存在')
        if job.status != Job.Status.RUNNING.value:
            raise ServiceException(ErrorCode.FAIL, '该任务无法暂停，当前任务状态：%s' % job.Status.label(job.status))
        job.status = Job.Status.SUSPENDED.value
        session.add(job)
        session.commit()
        scheduler.pause_job(job)

    @staticmethod
    @handle_exception
    def submit_job(file_bytes, config):
        """
        传输文件脚本
        :param file_bytes: 文件
        :param config:
        :return:
        """
        session = Session()
        try:
            job = Job()
            job.name = config['name']
            job.job_id = config['job_id']
            job.cron = config['cron']
            job.type = 1 if 'type' not in config else config['type']
            job.instance_cnt = 1 if 'instance_cnt' not in config else config['instance_cnt']
        except Exception as e:
            raise ServiceException(ErrorCode.PARAM_ERROR.value, '配置信息不正确')

        check_exist = session.query(Job).filter(Job.job_id == job.job_id).first()
        if check_exist is not None:
            raise ServiceException(ErrorCode.NOT_FOUND, '重复的job_id')

        file_name = os.path.dirname(os.path.abspath(__file__)) + '/../job/' + job.job_id + '.py'

        with open(file_name, 'wt') as f:
            f.write(file_bytes)

        session.add(job)
        job.create_time = datetime.now()
        session.commit()
        return job
