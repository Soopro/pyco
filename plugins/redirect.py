#coding=utf-8
from __future__ import absolute_import

def single_post_meta(post_meta,redirect_to):
    redirect_to["url"]=post_meta.get("redirect")
    return 