# coding=utf-8
from __future__ import absolute_import
import multiprocessing

bind = '127.0.0.1:5510'
workers = multiprocessing.cpu_count() * 2 + 1
accesslog = '/deploy/pyco_admin.access.log'
errorlog = '/deploy/pyco_admin.error.log'
pidfile = '/deploy/pyco_admin.pid'
raw_env = ''
