# coding=utf-8
from __future__ import absolute_import

_CONFIG = {}
_DEFAULT_INDEX_SLUG = 'index'
_DEFAULT_404_SLUG = 'error_404'


def config_loaded(config):
    global _CONFIG, _DEFAULT_INDEX_SLUG, _DEFAULT_404_SLUG
    _CONFIG = config
    _DEFAULT_INDEX_SLUG = config.get("DEFAULT_INDEX_SLUG")
    _DEFAULT_404_SLUG = config.get("DEFAULT_404_SLUG")
    return


def single_page_meta(page_meta, redirect_to):
    if not page_meta:
        return
    if page_meta["slug"] == _DEFAULT_INDEX_SLUG:
        page_meta["is_front"] = True
    if page_meta["slug"] == _DEFAULT_404_SLUG:
        page_meta["is_404"] = True

    return


def get_page_data(data, page_meta):
    if not data or not page_meta:
        return
    if data["slug"] == _DEFAULT_INDEX_SLUG:
        data["is_front"] = True
    if data["slug"] == _DEFAULT_404_SLUG:
        data["is_404"] = True
    return


def get_pages(pages, current_page):
    if not current_page:
        return
    for page in pages:
        if page["slug"] == current_page["slug"] \
                and page["content_type"] == current_page["content_type"]:
            page["is_current"] = True
    return
