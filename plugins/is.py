#coding=utf-8
from __future__ import absolute_import

_CONFIG = {}
_DEFAULT_INDEX_ALIAS = 'index'
_DEFAULT_404_ALIAS = 'error_404'

def config_loaded(config):
    global _CONFIG, _DEFAULT_INDEX_ALIAS, _DEFAULT_404_ALIAS
    _CONFIG = config
    _DEFAULT_INDEX_ALIAS = config.get("DEFAULT_INDEX_ALIAS")
    _DEFAULT_404_ALIAS = config.get("DEFAULT_404_ALIAS")
    return

def single_page_meta(page_meta, redirect_to):
    if page_meta["alias"] == _DEFAULT_INDEX_ALIAS:
        page_meta["is_front"] = True
    if page_meta["alias"] == _DEFAULT_404_ALIAS:
        page_meta["is_404"] = True
    
    return

def get_page_data(data, page_meta):
    if data["alias"] == _DEFAULT_INDEX_ALIAS:
        data["is_front"] = True
    if data["alias"] == _DEFAULT_404_ALIAS:
        data["is_404"] = True
    return


def get_pages(pages, current_page):
    for page in pages:
        if page["alias"] == current_page["alias"] \
        and page["content_type"] == current_page["content_type"]:
            page["is_current"] = True
    return