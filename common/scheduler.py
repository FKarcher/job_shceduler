#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'任务调度器'
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
