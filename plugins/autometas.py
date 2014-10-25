#coding=utf-8
from __future__ import absolute_import

def get_post_data(data, post_meta):
    for key in post_meta:
        data[key] = post_meta.get(key)
    return