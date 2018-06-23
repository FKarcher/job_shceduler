#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'some comment...'
__author__ = 'Jiateng Liang'

from apscheduler.schedulers.background import BlockingScheduler

scheduler = BlockingScheduler()


def start():
    scheduler.start()
