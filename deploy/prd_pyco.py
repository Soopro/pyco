# coding=utf-8
from __future__ import absolute_import
import multiprocessing

bind = '127.0.0.1:5500'
workers = multiprocessing.cpu_count() * 2 + 1
accesslog = '/deploy/pyco.access.log'
errorlog = '/deploy/pyco.error.log'
pidfile = '/deploy/pyco.pid'
raw_env = ''
