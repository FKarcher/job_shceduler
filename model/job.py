#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'Job Model'
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, Integer, String, BigInteger, DateTime
from sqlalchemy.ext.declarative import declarative_base
from model.db import Session

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
    start_date = Column(DateTime, comment='开始时间，默认立刻开始', default='2000-01-01 00:00:00')
    end_date = Column(DateTime, comment='结束时间，默认一直执行', default='2000-01-01 00:00:00')
    create_time = Column(DateTime, nullable=False)
    update_time = Column(DateTime, nullable=False, default=datetime.now())

    class Status(Enum):
        DELETED = -1
        STOPPED = 0
        RUNNING = 1
        SUSPENDED = 2



job = Job(name='sss', job_id='cn.s.')

session = Session()
session.add(job)

session.commit()
