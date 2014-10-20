#coding=utf-8
from __future__ import absolute_import

_DEFAULT_ADDITIONAL_METAS = ["nav","link","target","parent","thumbnail"]
_ADDITIONAL_METAS = None
_navs = []

def config_loaded(config):
    global _CONFIG, _ADDITIONAL_METAS

    _CONFIG = config
    _ADDITIONAL_METAS = set(_CONFIG.get("ADDITIONAL_METAS",[]) + _DEFAULT_ADDITIONAL_METAS)
    return


def get_post_data(data, post_meta):
    for key in _ADDITIONAL_METAS:
        data[key] = post_meta.get(key)
    return


def get_posts(posts, current_post, prev_post, next_post):
    global _navs
    _navs = [post for post in posts if post.get("nav")]
    return


def before_render(var,template):
    var["navigation"] = _navs
    return