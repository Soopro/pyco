#coding=utf-8
from __future__ import absolute_import
from urlparse import urlparse
import os

_CONFIG = {}
_DEFAULT_CONTENT_TYPE = 'page'
_URL = ''
_current_content_type = ''


def config_loaded(config):
    global _CONFIG
    _CONFIG = config
    return

            
def request_url(request, redirect_to):
    global _URL
    _URL = request.path
    return


def get_page_data(data, page_meta):
    data["type"] = page_meta.get("type")
    filter_auto_type(data, data.get("url"))
    return


def single_page_meta(page_meta, redirect_to):
    base_url = os.path.join(_CONFIG.get("BASE_URL"), '')
    page_url = os.path.join(base_url, _URL)
    filter_auto_type(page_meta, page_url)
    global _current_content_type
    _current_content_type = page_meta['type']
    return


def before_render(var, template):
    # content types
    content_types = _CONFIG["SITE"].get("content_types")
    current_content_type = var["meta"].get("type","")
    
    var["content_type"] = {
        'alias':current_content_type,
        'title':content_types.get(current_content_type)
    }
    return


# custome functions
def filter_auto_type(meta, page_url):
    if not meta.get("type"):
        url_parts = urlparse(page_url).path.split('/')
        if len(url_parts) > 2:
            meta["type"] = url_parts[1].lower()
        else:
            meta["type"] = _DEFAULT_CONTENT_TYPE
    meta["content_type"] = meta["type"]