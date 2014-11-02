#coding=utf-8
from __future__ import absolute_import
from plugin_helpers import generate_pagination

_CONFIG = {}
_DEFAULT_PAGINATION_LIMIT  = 10
_current_page = 1
_paged_pages = None
_pagination = None

def config_loaded(config):
    global _CONFIG
    _CONFIG = config
    return
    
def request_url(request, redirect_to):
    global _current_page
    try:
        _current_page = max(int(request.args.get("paged")), 1)
    except (ValueError, TypeError):
        _current_page = 1
    return

def get_pages(pages, current_page, prev_page, next_page):
    global _paged_pages, _pagination
    _paged_pages = _pagination = None
    
    if _current_page and isinstance(_current_page, int):
        limit = _CONFIG.get("PAGINATION_LIMIT", _DEFAULT_PAGINATION_LIMIT )
        _paged_pages, _pagination = generate_pagination(_current_page,limit,pages)
    return

def before_render(var,template):
    if not var.get('paged_pages') and not var.get('pagination'):
        var['results'] = _paged_pages
        var['pagination'] = _pagination
    return

#custom functions