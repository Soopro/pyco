# coding=utf-8

import re

CONTEXT = {}


def config_loaded(config):
    CONTEXT['config'] = config


def request_url(request):
    pass


def get_page_content(pack):
    pass


def get_page_meta(meta, redirect):
    pass


def get_pages(pages, current_page_id):
    pass


def before_render(context, template):
    pass


def after_render(rendered):
    pass
