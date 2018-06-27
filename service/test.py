#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'comment'
import time

from service.job_service import JobService

__author__ = 'Jiateng Liang'


def test_start_scheduler():
    JobService.start_scheduler()


def test_stop_scheduler():
    JobService.stop_scheduler()


def test_pause_scheduler():
    JobService.pause_scheduler()


def test_resume_scheduler():
    JobService.resume_scheduler()


def test_start_job(job_id):
    JobService.start_job(job_id)


def test_stop_job(job_id):
    JobService.stop_job(job_id)


def test_modify_job(job_id):
    JobService.modify_job(job_id, {'name': 'test', 'cron': '{"seconds": 8}'})


def test_pause_job(job_id):
    JobService.pause_job(job_id)


def test_submit_job():
    bytes = "#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\ndef run():"
    config = {
        'name': 'hahah',
        'job_id': 'jjjj',
        'cron': 'ddd'
    }
    JobService.submit_job(bytes, config)


# test_start_scheduler()
# time.sleep(3)
# test_start_job('test')
# time.sleep(3)
# test_pause_scheduler()
# time.sleep(3)
# test_resume_scheduler()
# time.sleep(3)
# time.sleep(3)

#  启动状态
# test_start_scheduler()
# time.sleep(3)
# test_start_job('test')
# time.sleep(3)
# test_pause_job('test')
# time.sleep(3)
# test_start_job('test')
# time.sleep(3)
# test_modify_job('test')
# time.sleep(3)
# test_stop_job('test')
# time.sleep(3)
# test_modify_job('test')
# time.sleep(3)
# # 暂停状态
# test_pause_scheduler()
# time.sleep(3)
# test_stop_job('test')
# time.sleep(3)
# test_start_job('test')
# time.sleep(3)
# test_pause_job('test')
# time.sleep(3)
# # 重启状态
# test_resume_scheduler()
# time.sleep(3)
# test_pause_job('test')
# time.sleep(3)
# test_start_job('test')
# time.sleep(3)
# # 停止状态
# test_stop_scheduler()
# time.sleep(3)
# test_pause_job('test')
# time.sleep(3)
# test_stop_job('test')
# time.sleep(3)
# test_start_job('test')



