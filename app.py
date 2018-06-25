#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'执行入口'

__author__ = 'Jiateng Liang'

from common.exception import handle_exception, ServiceException


@handle_exception
def scheduler_run():
    from common.scheduler import scheduler
    from service.job_service import JobService
    job_detect = JobService().get_job('job_detect')
    scheduler.add_job(job_detect)
    scheduler.start()



if __name__ == '__main__':
    scheduler_run()
