#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'任务调度器'
import importlib

from apscheduler.triggers.cron import CronTrigger

from model.job import Job

__author__ = 'Jiateng Liang'

from apscheduler.schedulers.background import BlockingScheduler


class Scheduler(object):
    def __init__(self):
        self._scheduler = BlockingScheduler()
        self._all_jobs = {}

    def start(self):
        self._scheduler.start()

    def add_job(self, job):
        if not job.job_id in self._all_jobs:
            self._all_jobs[job.job_id] = job
        self._all_jobs[job.job_id].status = Job.Status.RUNNING.value
        # 动态导入脚本
        script = importlib.import_module(job.job_id)

        self._scheduler.add_job(script.run, CronTrigger.from_crontab(job.cron), id=job.job_id,
                                start_date=job.start_date, end_date=job.end_date)

    def suspend_job(self, job):
        if job.job_id in self._all_jobs:
            self._all_jobs[job.job_id].status = Job.Status.SUSPENDED.value

    def stop_job(self, job):
        if job.job_id in self._all_jobs:
            self._all_jobs[job.job_id].status = Job.Status.STOPPED.value

    def remove_job(self, job):
        if job.job_id in self._all_jobs:
            del self._all_jobs[job.job_id]


scheduler = Scheduler()
