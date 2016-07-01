# coding=utf-8
from __future__ import absolute_import

from flask import g
from urlparse import urlparse
import os

_CONFIG = {}
_DEFAULT_CONTENT_TYPE = 'page'
_REQUEST_PATH = ''


def config_loaded(config):
    global _CONFIG
    _CONFIG = config
    config['SHORT_ATTR_KEY'].update({
        'type': 'content_type'
    })
    return


def request_url(request, redirect_to):
    return


def get_page_data(data, page_meta):
    if not data or not page_meta:
        return
    data["type"] = page_meta.get("type")
    filter_auto_type(data, data.get("url", '').replace(g.curr_base_url, ''))
    data["content_type"] = data["type"]
    return


def single_page_meta(page_meta, redirect_to):
    if not page_meta:
        return
    filter_auto_type(page_meta, g.request_path)
    page_meta["content_type"] = page_meta["type"]
    return


def before_render(var, template):
    if not template:
        return
    # content types
    content_types = _CONFIG["SITE"].get("content_types")
    current_content_type = var["meta"].get("type", "")

    var["content_type"] = {
        'slug': current_content_type,
        'title': content_types.get(current_content_type)
    }
    return


# custome functions
def filter_auto_type(meta, page_path):
    if not meta.get("type"):
        path_parts = page_path.split('/')
        if len(path_parts) > 2:
            meta["type"] = path_parts[1].lower()
        else:
            meta["type"] = _DEFAULT_CONTENT_TYPE
