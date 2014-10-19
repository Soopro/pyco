#coding=utf-8
from __future__ import absolute_import


def plugins_loaded():
    print "plugin loaded"
    return


def config_loaded(config):
    print "config loaded"
    return


def request_url(request, redirect_to):
    print "request url"
    return


def before_load_content(file):
    print "before load content"
    return


def after_load_content(file, content):
    print "after load content"
    return


def before_404_load_content(file):
    print "before 404 load content"
    return


def after_404_load_content(file, content):
    print "after 404 load content"
    return


def before_read_post_meta(headers):
    print "before read post meta"
    return


def single_post_meta(post_meta, redirect_to):
    print "post meta"
    return


def before_parse_content(content):
    print "before parse content"
    return


def after_parse_content(content):
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


def before_render(var,template):
    print "before render"
    return


def after_render(output):
    print "after render"
    return