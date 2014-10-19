#coding=utf-8
from __future__ import absolute_import
from plugin_helpers import generate_pagination

_CONFIG = {}
_DEFAULT_PAGINATION_LIMIT  = 10
_current_page = 1
_paged_posts = None
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

def get_posts(posts, current_post, prev_post, next_post):
    global _paged_posts, _pagination
    _paged_posts = _pagination = None
    
    if _current_page and isinstance(_current_page, int):
        limit = _CONFIG.get("PAGINATION_LIMIT", _DEFAULT_PAGINATION_LIMIT )
        _paged_posts, _pagination = generate_pagination(_current_page,limit,posts)
    return

def before_render(var,template):
    if not var.get('paged_posts') and not var.get('pagination'):
        var['results'] = _paged_posts
        var['pagination'] = _pagination
    return

#custom functions