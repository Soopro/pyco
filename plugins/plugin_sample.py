#coding=utf-8
from __future__ import absolute_import


def plugins_loaded():
    print "plugin loaded"
    return


def config_loaded(config):
    print "config loaded"
    return


def request_url(url):
    print "request url"
    return


def before_load_content():
    print "before load content"
    return


def after_load_content():
    print "after load content"
    return


def before_404_load_content():
    print "before 404 load content"
    return


def after_404_load_content():
    print "after 404 load content"
    return


def before_read_post_meta():
    print "before read post meta"
    return


def single_post_meta(post_meta):
    print "post meta"
    return


def before_parse_content():
    print "before parse content"
    return


def after_parse_content():
    print "after parse content"
    return


def get_post_data(data, post_meta):
    print "get post data"
    return


def get_posts(posts, current_post, prev_post, next_post):
    print "get posts"
    return


# def before_template_register():
#     print "before template register"
#     return


def before_render():
    print "before render"
    return


def after_render():
    print "after render"
    return