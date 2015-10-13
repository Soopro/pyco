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


def before_read_page_meta(meta_string):
    print "before read page meta"
    return


def after_read_page_meta(headers):
    print "after read page meta"
    return


def single_page_meta(page_meta, redirect_to):
    print "page meta"
    return


def before_parse_content(content):
    print "before parse content"
    return


def after_parse_content(content):
    print "after parse content"
    return

def get_page_data(data, page_meta):
    print "get page data"
    return


def get_pages(pages, current_page):
    print "get pages"
    return


# def before_template_register():
#     print "before template register"
#     return


def before_render(var, template):
    print "before render"
    return


def after_render(output):
    print "after render"
    return