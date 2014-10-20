#coding=utf-8
from __future__ import absolute_import

_CONFIG = {}

def config_loaded(config):
    global _CONFIG
    _CONFIG = config
    return

def get_post_data(data, post_meta):
    data["draft"] = post_meta.get("draft")
    if isinstance(data["draft"], (str,unicode)) and data["draft"].lower() == "true":
        data["draft"] = True
    else:
        data["draft"] = False
    return

def get_posts(posts, current_post, prev_post, next_post):
    tmp_posts = [post for post in posts if not post.get("draft")]
    
    del posts[:]
    for post in tmp_posts:
        posts.append(post)
    return