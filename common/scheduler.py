#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'任务调度器, job_id与定时任务脚本名称对应，唯一。所有任务脚本需要制定唯一入口run()'
import importlib

from apscheduler.events import EVENT_JOB_ADDED, EVENT_JOB_REMOVED, EVENT_JOB_MODIFIED, EVENT_JOB_EXECUTED, \
    EVENT_JOB_ERROR, EVENT_SCHEDULER_STARTED, EVENT_SCHEDULER_SHUTDOWN, EVENT_SCHEDULER_PAUSED, EVENT_SCHEDULER_RESUMED

from common.exception import ServiceException, ErrorCode
from model.job import Job

from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
from config.config import config
import copy
from common.log import logger

__author__ = 'Jiateng Liang'

STOPPED = 0
RUNNING = 1
PAUSED = 2


class Scheduler(object):
    def __init__(self):
        self._scheduler = BackgroundScheduler(executors=config.EXECUTORS, job_defaults=config.JOB_DEFAULTS,
                                              timezone=config.TIME_ZONE)
        # self._all_jobs = {}

        self._scheduler.add_listener(self._on_job_add, EVENT_JOB_ADDED)
        self._scheduler.add_listener(self._on_job_remove, EVENT_JOB_REMOVED)
        self._scheduler.add_listener(self._on_job_modify, EVENT_JOB_MODIFIED)
        self._scheduler.add_listener(self._on_job_execute, EVENT_JOB_EXECUTED)
        self._scheduler.add_listener(self._on_job_error, EVENT_JOB_ERROR)
        self._scheduler.add_listener(self._on_scheduler_start, EVENT_SCHEDULER_STARTED)
        self._scheduler.add_listener(self._on_scheduler_stop, EVENT_SCHEDULER_SHUTDOWN)
        self._scheduler.add_listener(self._on_scheduler_pause, EVENT_SCHEDULER_PAUSED)
        self._scheduler.add_listener(self._on_scheduler_resume, EVENT_SCHEDULER_RESUMED)

    def start(self):
        if self.status() != STOPPED:
            raise ServiceException(ErrorCode.FAIL, '无法启动调度器，调度器不在停止状态')
        self._scheduler.start()

    def shutdown(self, waited=True):
        """
        :param waited: 等待所有任务执行结束后再停止
        :return:
        """
        if self.status() != RUNNING:
            raise ServiceException(ErrorCode.FAIL, '无法停止调度器，调度器不在运行状态')
        self._scheduler.shutdown(wait=waited)

    def pause(self):
        if self.status() != RUNNING:
            raise ServiceException(ErrorCode.FAIL, '无法暂停调度器，调度器不在运行状态')
        self._scheduler.pause()

    def resume(self):
        if self.status() != PAUSED:
            raise ServiceException(ErrorCode.FAIL, '无法重启调度器，调度器不在暂停状态')
        self._scheduler.resume()

    def status(self):
        """
        获取当前调度器状态
        0 停止，1 运行，2暂停
        :return:
        """
        return self._scheduler.state

    def add_job(self, task):
        if self.status() != RUNNING:
            raise ServiceException(ErrorCode.FAIL, '启动任务%s失败，调度器没有运行' % task.job_id)
        # 判断是否已经加入了调度器
        if self._scheduler.get_job(task.job_id) is None:
            # 动态导入脚本
            script = importlib.import_module('job.' + task.job_id)

            if script is None or not hasattr(script, 'run'):
                raise ServiceException(ErrorCode.FAIL, ("%s任务没有run方法" % task.job_id))

            try:
                cron_dict = eval(task.cron)
            except Exception as e:
                raise ServiceException(ErrorCode.FAIL, ("%s任务cron规则错误" % task.job_id), str(e))

            try:
                if task.type == Job.Type.INTERVAL.value:
                    self._scheduler.add_job(script.run, 'interval', **cron_dict, id=task.job_id,
                                            max_instances=task.instance_cnt)
                elif task.type == Job.Type.CRON.value:
                    self._scheduler.add_job(script.run, 'cron', **cron_dict, id=task.job_id,
                                            max_instances=task.instance_cnt)
            except Exception as e:
                raise ServiceException(ErrorCode.INTERNAL_ERROR, ("加入任务%s失败" % task.job_id), str(e))
        else:
            raise ServiceException(ErrorCode.FAIL, ("任务%s已存在" % task.job_id))

    def pause_job(self, task):
        current_job = self._scheduler.get_job(task.job_id)
        if current_job is not None:
            # 如果不在运行中
            if current_job.next_run_time is None:
                raise ServiceException(ErrorCode.FAIL,
                                       '无法暂停任务%s, 该任务现在已经停止' % (task.job_id))
            else:
                self._scheduler.pause_job(task.job_id)
        else:
            raise ServiceException(ErrorCode.FAIL, ("任务%s不存在" % task.job_id))

    def resume_job(self, task):
        current_job = self._scheduler.get_job(task.job_id)
        if current_job is not None:
            # 如果在运行中
            if current_job.next_run_time is not None:
                raise ServiceException(ErrorCode.FAIL,
                                       '无法重启任务%s, 该任务的现在已经在运行' % (task.job_id))
            else:
                self._scheduler.resume_job(task.job_id)
        else:
            raise ServiceException(ErrorCode.FAIL, ("任务%s不存在" % task.job_id))

    # def modify_job(self, task):
    #     current_job = self._scheduler.get_job(task.job_id)
    #     if current_job is not None:
    #         try:
    #             cron_dict = eval(task.cron)
    #         except Exception as e:
    #             raise ServiceException(ErrorCode.FAIL, ("%s任务cron规则错误" % task.job_id), str(e))
    #
    #         try:
    #             if task.type == Job.Type.INTERVAL.value:
    #                 self._scheduler.reschedule_job(task.job_id, trigger='interval', **cron_dict,
    #                                                max_instances=task.instance_cnt)
    #             elif task.type == Job.Type.CRON.value:
    #                 self._scheduler.reschedule_job(task.job_id, trigger='cron', **cron_dict,
    #                                                max_instances=task.instance_cnt)
    #         except Exception as e:
    #             raise ServiceException(ErrorCode.INTERNAL_ERROR, ("修改任务%s失败" % task.job_id), str(e))
    #     else:
    #         raise ServiceException(ErrorCode.FAIL, ("任务%s不存在" % task.job_id))

    def remove_job(self, task):
        current_job = self._scheduler.get_job(task.job_id)
        if current_job is not None:
            self._scheduler.remove_job(task.job_id)
        else:
            raise ServiceException(ErrorCode.FAIL, ("任务%s不存在" % task.job_id))

    ###### Listener ######
    def _on_job_add(self, event):
        from service.job_service import JobService
        job_id = event.job_id
        job = JobService.get_job(job_id)
        # 有自动加入的情况
        if job.status != job.Status.RUNNING.value:
            JobService.change_job_status(job_id, job.Status.RUNNING)
            job.status = job.Status.RUNNING.value
        logger.info('定时任务%s加入了调度器，信息：%s' % (job_id, str(job)))

    def _on_job_remove(self, event):
        from service.job_service import JobService
        job_id = event.job_id
        job = JobService.get_job(job_id)
        # 有自动删除的情况
        if job.status != job.Status.STOPPED.value:
            JobService.change_job_status(job_id, job.Status.STOPPED)
        logger.info('定时任务%s被移除了调度器，信息：%s' % (job_id, str(job)))

    def _on_job_modify(self, event):
        from service.job_service import JobService
        job_id = event.job_id
        job = self._scheduler.get_job(job_id)
        if job.next_run_time is None:
            job = JobService.get_job(job_id)
            logger.info('定时任务%s已暂停，信息：%s' % (job_id, str(job)))
            if job.status != job.Status.SUSPENDED.value:
                JobService.change_job_status(job_id, job.Status.SUSPENDED)
        else:
            logger.info('定时任务%s被修改或重启了并正在运行中，信息：%s' % (job_id, str(job)))

    def _on_job_error(self, event):
        from service.job_service import JobService
        e = event.exception
        job_id = event.job_id
        logger.warn('定时任务%s发生错误，将被移除调度器' % job_id)
        logger.error(str(e))
        task = JobService.get_job(job_id)
        self.remove_job(task)

    def _on_job_execute(self, event):
        from service.job_service import JobService
        job_id = event.job_id
        logger.info('定时任务%s开始执行' % job_id)
        JobService.add_executed_times(job_id, 1)

    def _on_scheduler_start(self, event):
        logger.info('调度器开始执行')

    def _on_scheduler_pause(self, event):
        logger.info('调度器暂停')

    def _on_scheduler_resume(self, event):
        logger.info('调度器重启')

    def _on_scheduler_stop(self, event):
        logger.info('调度器停止')

    def next_run_time(self, job_id):

        return self._scheduler.get_job(job_id).next_run_time

# 全局唯一的scheduler，所有scheduler从这里引入
scheduler = Scheduler()
