#coding=utf-8
from __future__ import absolute_import

_CONFIG = {}
_ORDER_DESC = False
_ORDER_BY = 'date'

def config_loaded(config):
    global _CONFIG, _ORDER_DESC, _ORDER_BY

    _CONFIG = config

    if _CONFIG.get('POST_ORDER') == 'desc':
        _ORDER_DESC = True

    _ORDER_BY = _CONFIG.get('POST__ORDER_BY') or _ORDER_BY
    return

def get_post_data(data, post_meta):
    data["order"] = post_meta.get("order")
    return

def get_posts(posts, current_post, prev_post, next_post):
    for post in posts:
        try: 
            order = int(post.get('order'))
        except Exception:
            order = None

        post['order'] =  order or 0
    _posts=sorted(posts,key=lambda x: (x['order'], x[_ORDER_BY]),reverse=_ORDER_DESC)
    
    del posts[:]
    for post in _posts:
        posts.append(post)
    return