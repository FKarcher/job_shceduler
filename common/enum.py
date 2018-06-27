#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'枚举公共操作'


def labels(cls):
    @classmethod
    def to_str(cls, val):
        if val is None:
            return ''
        elif hasattr(cls, '__labels__'):
            return cls.__labels__.get(int(val))
        else:
            return str(val)

    cls.label = to_str
    return cls



    # 使用样例

    # @labels
    # class Status(Enum):
    #     """
    #     -1删除 0停止 1执行 2暂停
    #     """
    #     DELETED = -1
    #     STOPPED = 0
    #     RUNNING = 1
    #     SUSPENDED = 2
    #
    #     __labels__ = {
    #         DELETED: '已删除',
    #         STOPPED: '已停止',
    #         RUNNING: '运行中',
    #         SUSPENDED: '已暂停'
    #     }

    # Model.Status.label(1)