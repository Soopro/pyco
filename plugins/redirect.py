# coding=utf-8
from __future__ import absolute_import

_CONFIG = {}


def config_loaded(config):
    global _CONFIG
    _CONFIG = config
    return


def single_page_meta(page_meta, redirect_to):
    if not page_meta:
        return
    content_type = page_meta.get("type")
    if content_type.startswith('_'):
        redirect_to["url"] = _CONFIG.get("DEFAULT_404_SLUG")
    else:
        redirect_to["url"] = page_meta.get("redirect")
    return
