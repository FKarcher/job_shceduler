#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'数据库加载'
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

__author__ = 'Jiateng Liang'
from config.config import config

engine = create_engine(config.DB_URL_CONNECTION, encoding='utf-8')
engine.echo = config.ENABLE_SQL_LOG
Session = sessionmaker(bind=engine)

# 全局唯一session 相当于一个scoped_session Service层严禁new Session()
session = Session()
