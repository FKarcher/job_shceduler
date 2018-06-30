#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'thrift job对外接口'
import json

from common.exception import handle_exception
from service.job_service import JobService

__author__ = 'Jiateng Liang'


class JobController:

    @handle_exception(throwable=True)
    def start_scheduler(self):
        return JobService.start_scheduler()

    @handle_exception(throwable=True)
    def stop_scheduler(self):
        return JobService.stop_scheduler()

    @handle_exception(throwable=True)
    def pause_scheduler(self):
        return JobService.pause_scheduler()

    @handle_exception(throwable=True)
    def resume_scheduler(self):
        return JobService.resume_scheduler()

    @handle_exception(throwable=True)
    def start_job(self, job_id):
        return JobService.start_job(job_id)

    @handle_exception(throwable=True)
    def stop_job(self, job_id):
        return JobService.stop_job(job_id)

    @handle_exception(throwable=True)
    def pause_job(self, job_id):
        return JobService.pause_job(job_id)

    @handle_exception(throwable=True)
    def modify_job(self, job_id, config):
        return JobService.modify_job(job_id, config)

    @handle_exception(throwable=True)
    def submit_job(self, file_bytes, config):
        return JobService.submit_job(file_bytes, config)

    @handle_exception(throwable=True)
    def status(self):
        return JobService.status()

