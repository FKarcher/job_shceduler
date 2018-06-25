#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'配置文件入口 from config.config import config'
__author__ = 'Jiateng Liang'
import sys

if len(sys.argv) <= 1:
    import config.config_dev as config
elif sys.argv[1] == 'dev':
    import config.config_dev as config
elif sys.argv[1] == 'test':
    import config.config_test as config
elif sys.argv[1] == 'prod':
    import config_prod as config
