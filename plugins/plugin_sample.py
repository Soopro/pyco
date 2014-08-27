#coding=utf-8
from __future__ import absolute_import


def plugins_loaded():
    print "plugin loaded"
    return


def config_loaded():
    print "config loaded"
    return


def request_url():
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


def before_read_file_meta():
    print "before read file meta"
    return


def file_meta():
    print "file meta"
    return


def before_parse_content():
    print "before parse content"
    return


def after_parse_content():
    print "after parse content"
    return


def get_page_data():
    print "get page data"
    return


def get_pages():
    print "get pages"
    return


def before_template_register():
    print "before template register"
    return


def before_render():
    print "before render"
    return


def after_render():
    print "after render"
    return