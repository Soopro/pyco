#coding=utf-8
from __future__ import absolute_import

_ADDITIONAL_METAS = ['nav','link','target','parent','thumbnail']
_navs = []

def get_post_data(data, post_meta):
    for key in _ADDITIONAL_METAS:
        data[key] = post_meta.get(key)
    return

def get_posts(posts, current_post, prev_post, next_post):
    global _navs
    _navs = [post for post in posts if post.get('nav')]
    return

def before_render(var,template):
    var['navigation'] = _navs
    return