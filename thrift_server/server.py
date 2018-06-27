#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'thrift server'
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.transport import TSocket, TTransport

from common.log import logger
from thrift_server.handler.job_handler import JobController
from thrift_server.thrift_gen import JobRPCService

__author__ = 'Jiateng Liang'

from config.config import config


def run():
    job_controller = JobController()
    processor = JobRPCService.Processor(job_controller)
    transport = TSocket.TServerSocket(config.RPC_HOST, config.RPC_PORT)  # 传输层协议
    transport_factory = TTransport.TBufferedTransportFactory()  # 缓冲
    protocol_factory = TBinaryProtocol.TBinaryProtocolFactory()  # 消息协议：json

    server = TServer.TSimpleServer(processor, transport, transport_factory, protocol_factory)

    logger.info("******** 启动Thrift server ********")
    server.serve()
