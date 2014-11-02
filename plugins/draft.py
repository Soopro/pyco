#coding=utf-8
from __future__ import absolute_import

_CONFIG = {}

def config_loaded(config):
    global _CONFIG
    _CONFIG = config
    return

def get_page_data(data, page_meta):
    data["draft"] = page_meta.get("draft")
    if isinstance(data["draft"], (str,unicode)) and data["draft"].lower() == "true":
        data["draft"] = True
    else:
        data["draft"] = False
    return

def get_pages(pages, current_page, prev_page, next_page):
    for page in pages:
        if page.get("draft"):
            i = pages.index(page)
            pages.pop(i)
    return