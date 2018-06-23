#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'执行入口'
__author__ = 'Jiateng Liang'
import sys

if len(sys.argv) <= 1:
    import config.config_dev as config
elif sys.argv[1] == 'dev':
    import config.config_dev as config
elif sys.argv[1] == 'test':
    import config.config_test as config
elif sys.argv[1] == 'prod':
    import config.config as config

# if __name__ == '__main__':
