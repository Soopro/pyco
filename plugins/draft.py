#coding=utf-8
from __future__ import absolute_import

_CONFIG = {}


def config_loaded(config):
    global _CONFIG
    _CONFIG = config
    return

def single_page_meta(page_meta, redirect_to):
    page_meta['status'] = int(page_meta.get("status",1))
    return

def get_page_data(data, page_meta):
    data["status"] = page_meta.get("status")
    return


def get_pages(pages, current_page):
    for page in pages:
        if page.get("status") not 1:
            i = pages.index(page)
            pages.pop(i)
    return