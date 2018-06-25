#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'Job Model'
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, BigInteger, DateTime
from sqlalchemy.ext.declarative import declarative_base
from common.enum import labels

__author__ = 'Jiateng Liang'

BaseModel = declarative_base()


class Job(BaseModel):
    __tablename__ = "job"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(50), nullable=False, comment='任务名称')
    job_id = Column(String(50), nullable=False, comment='程序指定的job_id', unique=True)
    status = Column(Integer, nullable=False, comment='-1删除 0停止 1执行 2暂停', default=0)
    executed_times = Column(BigInteger, nullable=False, comment='执行次数', default=0)
    cron = Column(String(255), comment='执行规则', default='')
    type = Column(Integer, default=1, comment='执行规则类型，1 interval 2 cron')
    start_date = Column(DateTime, comment='开始时间，默认立刻开始', default='2000-01-01 00:00:00')
    end_date = Column(DateTime, comment='结束时间，默认一直执行', default='2000-01-01 00:00:00')
    instance_cnt = Column(Integer, nullable=False, default=1, comment='实例运行数量，最大为5')
    create_time = Column(DateTime, nullable=False)
    update_time = Column(DateTime, nullable=False, default=datetime.now())

    @labels
    class Status(Enum):
        """
        -1删除 0停止 1执行 2暂停
        """
        DELETED = -1
        STOPPED = 0
        RUNNING = 1
        SUSPENDED = 2

        __labels__ = {
            DELETED: '已删除',
            STOPPED: '已停止',
            RUNNING: '运行中',
            SUSPENDED: '已暂停'
        }

        ALL = [DELETED, STOPPED, RUNNING, SUSPENDED]

    @labels
    class Type(Enum):
        """
        定时策略
        """
        INTERVAL = 1
        CRON = 2

        __labels__ = {
            INTERVAL: 'Interval',
            CRON: 'Cron',
        }

    def __repr__(self) -> str:
        return str({'id': self.id, 'job_id': self.job_id, 'name': self.name, 'status': Job.Status.label(self.status),
                    'executed_times': self.executed_times, 'cron': self.cron, 'type': Job.Type.label(self.type),
                    'instance_cnt': self.instance_cnt,
                    'create_time': self.create_time, 'update_time': self.update_time})
