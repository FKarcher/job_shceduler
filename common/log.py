#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'日志'
from logging.handlers import TimedRotatingFileHandler

__author__ = 'Jiateng Liang'
from config.config import config

import logging

logger = logging.getLogger(config.LOG_NAME)

fh = TimedRotatingFileHandler(filename=config.LOG_PATH, when="D", interval=1)

if config.LOG_LEVEL == 'DEBUG':
    logger.setLevel(logging.DEBUG)
    fh.setLevel(logging.DEBUG)
elif config.LOG_LEVEL == 'INFO':
    logger.setLevel(logging.INFO)
    fh.setLevel(logging.INFO)
elif config.LOG_LEVEL == 'WARN':
    logger.setLevel(logging.WARN)
    fh.setLevel(logging.WARN)
elif config.LOG_LEVEL == 'ERROR':
    logger.setLevel(logging.ERROR)
    fh.setLevel(logging.ERROR)

formatter = logging.Formatter(config.LOG_FORMAT, config.LOG_DATE_FORMAT)

fh.setFormatter(formatter)
logger.addHandler(fh)

if config.LOG_CONSOLE:
    console = logging.StreamHandler()
    console.setLevel(config.LOG_LEVEL)
    console.setFormatter(formatter)
    logger.addHandler(console)
