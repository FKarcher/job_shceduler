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
from common.db import session

__author__ = 'Jiateng Liang'


class JobService(object):

    @staticmethod
    @handle_exception(throwable=False)
    def list_jobs_by_status(status=None):
        """
        列出所有Job
        :param status: -1删除 0停止 1执行 2暂停 3待加入
        :return: [Job]
        """
        if status is None:
            return session.query(Job).all()

        return session.query(Job).filter(Job.status == status).all()

    @staticmethod
    @handle_exception(throwable=False)
    def get_job(job_id):
        """
        根据job_id获取job
        :param job_id:
        :return:
        """
        job = session.query(Job).filter(Job.job_id == job_id).first()
        if job is None:
            raise ServiceException(ErrorCode.NOT_FOUND, '该任务不存在')
        return job

    @staticmethod
    @handle_exception(throwable=False)
    def insert_job(job):
        if not job or not job.job_id or not job.name:
            raise ServiceException(ErrorCode.PARAM_ERROR, 'job参数错误，job_id或name不能为空')
        if session.query(Job).filter(Job.job_id == job.job_id).first() is not None:
            raise ServiceException(ErrorCode.FAIL, 'job_id重复，该任务已经存在')
        job.create_time = datetime.now()
        session.add(job)
        session.commit()
        return job.job_id

    @staticmethod
    @handle_exception(throwable=False)
    def add_executed_times(job_id, cnt):
        """
        增加任务运行次数
        :param job_id: job_id
        :param cnt: 次数
        :return:
        """
        job = JobService.get_job(job_id)
        job.executed_times += cnt
        session.add(job)
        session.commit()
        return job.job_id

    @staticmethod
    @handle_exception(throwable=False)
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
        job = JobService.get_job(job_id)
        job.status = status.value
        session.add(job)
        session.commit()
        return job.job_id

    @staticmethod
    @handle_exception(throwable=False)
    def stop_all_jobs():
        """
        停止所有job
        :return:
        """

        jobs = JobService.list_jobs_by_status()
        for job in jobs:
            job.status = Job.Status.STOPPED.value
            session.add(job)
        session.commit()


    @staticmethod
    def start_scheduler():
        """
        启动调度器
        :return:
        """
        scheduler.start()

    @staticmethod
    def stop_scheduler():
        """
        停止调度器
        :return:
        """
        jobs = session.query(Job).filter(
            or_(Job.status == Job.Status.RUNNING.value, Job.status == Job.Status.SUSPENDED.value)).all()
        for job in jobs:
            job.status = Job.Status.STOPPED.value
            session.add(job)
        scheduler.shutdown()
        session.commit()

    @staticmethod
    def pause_scheduler():
        """
        暂停调度器
        :return:
        """
        jobs = JobService.list_jobs_by_status(Job.Status.RUNNING.value)
        for job in jobs:
            job.status = Job.Status.SUSPENDED.value
            session.add(job)
        scheduler.pause()
        session.commit()

    @staticmethod
    def resume_scheduler():
        """
        重启调度器
        :return:
        """
        jobs = JobService.list_jobs_by_status(Job.Status.SUSPENDED.value)
        for job in jobs:
            job.status = Job.Status.RUNNING.value
            session.add(job)
        scheduler.resume()
        session.commit()

    @staticmethod
    def start_job(job_id):
        """
        开启一个停止的任务或者暂停的任务
        :param job_id:
        :return:
        """
        if scheduler.status() != RUNNING:
            raise ServiceException(ErrorCode.FAIL, '无法启动任务，调度器没有运行')
        job = JobService.get_job(job_id)
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
    def stop_job(job_id):
        """
        任务停止
        :param job_id:
        :return:
        """
        job = JobService.get_job(job_id)
        if job.status == Job.Status.STOPPED.value:
            raise ServiceException(ErrorCode.FAIL, '该任务已经停止')
        job.status = Job.Status.STOPPED.value
        session.add(job)
        session.commit()
        scheduler.remove_job(job)


    @staticmethod
    def status():
        """
        获取当前状态
        0 停止，1 运行，2暂停
        :return:
        """
        return scheduler.status()

    @staticmethod
    def modify_job(job_id, config):
        """
        修改任务规则
        :param job_id:
        :return:
        """
        job = JobService.get_job(job_id)
        if job.status != Job.Status.STOPPED.value:
            raise ServiceException(ErrorCode.FAIL, '请先停止任务，当前状态：' + job.Status.label(job.status))
        try:
            config = eval(config)
            job.name = config['name'] if 'name' in config else job.name
            job.cron = config['cron'] if 'cron' in config else job.cron
            job.type = config['type'] if 'type' in config else job.type
            job.instance_cnt = config['instance_cnt'] if 'instance_cnt' in config else job.instance_cnt
        except Exception as e:
            raise ServiceException(ErrorCode.PARAM_ERROR.value, '配置信息不正确')
        session.add(job)
        session.commit()

    @staticmethod
    def pause_job(job_id):
        """
        暂停任务
        :param job_id:
        :return:
        """
        job = JobService.get_job(job_id)
        if job.status != Job.Status.RUNNING.value:
            raise ServiceException(ErrorCode.FAIL, '该任务无法暂停，当前任务状态：%s' % job.Status.label(job.status))
        job.status = Job.Status.SUSPENDED.value
        session.add(job)
        session.commit()
        scheduler.pause_job(job)


    @staticmethod
    def submit_job(file_bytes, config):
        """
        传输文件脚本
        :param file_bytes: 文件
        :param config:
        :return:
        """
        try:
            config = eval(config)
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
        return job.job_id
