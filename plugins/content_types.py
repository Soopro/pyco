#coding=utf-8
from __future__ import absolute_import

def before_read_file_meta(cfg, env, ctx):
    print env
    return