# coding=utf-8
from __future__ import absolute_import
import multiprocessing

bind = '127.0.0.1:9009'
workers = multiprocessing.cpu_count() * 2 + 1
accesslog = '/data/deployment_data/totoro/log/totoro_admin.access.log'
errorlog = '/data/deployment_data/totoro/log/totoro_admin.error.log'
pidfile = '/data/deployment_data/totoro/totoro_admin.pid'
raw_env = 'TOTORO_CONFIG_NAME=production'
