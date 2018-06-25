#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'任务调度器, job_id与定时任务脚本名称对应，唯一。所有任务脚本需要制定唯一入口run()'
import importlib

from common.exception import ServiceException, ErrorCode
from model.job import Job

__author__ = 'Jiateng Liang'

from apscheduler.schedulers.background import BlockingScheduler
from config.config import config
import copy


class Scheduler(object):

    def __init__(self):
        self._scheduler = BlockingScheduler(executors=config.EXECUTORS, job_defaults=config.JOB_DEFAULTS,
                                            timezone=config.TIME_ZONE)
        self._all_jobs = {}

    def start(self):
        self._scheduler.start()

    def shutdown(self, waited=True):
        """
        :param waited: 等待所有任务执行结束后再停止
        :return:
        """
        self._scheduler.shutdown(wait=waited)

    def add_job(self, task):
        if task.job_id not in self._all_jobs:
            self._all_jobs[task.job_id] = task
            self._all_jobs[task.job_id].status = Job.Status.RUNNING.value
            # 动态导入脚本
            script = importlib.import_module('job.' + task.job_id)

            if script is None or script.run is None:
                raise ServiceException(ErrorCode.FAIL, ("%s任务没有run方法" % task.job_id))

            try:
                cron_dict = eval(task.cron)
            except Exception as e:
                raise ServiceException(ErrorCode.FAIL, ("%s任务cron规则错误" % task.job_id), str(e))

            if task.type == Job.Type.INTERVAL.value:
                self._scheduler.add_job(script.run, 'interval', **cron_dict, id=task.job_id,
                                        max_instances=task.instance_cnt)
            elif task.type == Job.Type.CRON.value:
                self._scheduler.add_job(script.run, 'cron', **cron_dict, id=task.job_id,
                                        max_instances=task.instance_cnt)

    def suspend_job(self, task):
        if task.job_id in self._all_jobs:
            self._scheduler.pause_job(task.job_id)
            self._all_jobs[task.job_id].status = Job.Status.SUSPENDED.value

    def resume_job(self, task):
        if task.job_id in self._all_jobs:
            self._scheduler.resume_job(task.job_id)
            self._all_jobs[task.job_id].status = Job.Status.RUNNING.value

    def remove_job(self, task):
        if task.job_id in self._all_jobs:
            self._scheduler.remove_job(task.job_id)
            del self._all_jobs[task.job_id]

    def get_jobs(self):
        return copy.deepcopy(self._all_jobs)

    def get_job(self, job_id):
        return copy.deepcopy(self._all_jobs[job_id])


# 全局唯一的scheduler，所有scheduler从这里引入
scheduler = Scheduler()
