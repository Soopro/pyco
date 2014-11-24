#coding=utf-8
from __future__ import absolute_import


def get_page_data(data, page_meta):
    for key in page_meta:
        data[key] = page_meta.get(key)
    return