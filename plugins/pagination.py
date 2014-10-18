#coding=utf-8
from __future__ import absolute_import

_CONFIG = {}
_DEFAULT_PAGINATION_LIMIT  = 10
_current_page = 1
_paged_posts = dict()
_pagination = dict()

def config_loaded(config):
    _CONFIG.update(config)
    return
    
def request_url(request):
    global _current_page
    try:
        _current_page = max(int(request.args.get("paged")), 1)
    except (ValueError, TypeError):
        _current_page = 1
    return


def get_posts(posts, current_post, prev_post, next_post):
    global _current_page
    if _current_page and isinstance(_current_page, int):
        _pagination_limit = _CONFIG.get("PAGINATION_LIMIT", _DEFAULT_PAGINATION_LIMIT )
        total = page_count(_pagination_limit, len(posts))
        _current_page = min(_current_page, total)
        start = (_current_page-1)*_pagination_limit
        end = _current_page*_pagination_limit
        
        global _paged_posts
        _paged_posts = posts[start:end]
        
        global _pagination
        _pagination["current_page"] = _current_page
        _pagination["has_prev_page"] = _current_page > 1
        _pagination["has_next_page"] = _current_page < total
    return

def page_count(_pagination_limit, total):
    return max((total+_pagination_limit-1)/_pagination_limit, 1)

def before_render(var,template):
    var['current_page_posts'] = _paged_posts
    var['pagination'] = _pagination
    return