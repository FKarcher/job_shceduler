#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'comment'
import time

from common.scheduler import scheduler
from service.job_service import JobService

__author__ = 'Jiateng Liang'


job = JobService.get_job('test')
scheduler.start()
scheduler.add_job(job)
time.sleep(13)
scheduler.pause_job(job)
time.sleep(100)
