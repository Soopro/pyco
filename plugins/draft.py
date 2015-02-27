#coding=utf-8
from __future__ import absolute_import

_CONFIG = {}


def config_loaded(config):
    global _CONFIG
    _CONFIG = config
    return


def get_page_data(data, page_meta):
    data["status"] = page_meta.get("status")
    if isinstance(data["status"], (str, unicode)) \
    and data["status"].lower() == "true":
        data["status"] = True
    else:
        data["stauts"] = False
    return


def get_pages(pages, current_page):
    for page in pages:
        if page.get("status"):
            i = pages.index(page)
            pages.pop(i)
    return