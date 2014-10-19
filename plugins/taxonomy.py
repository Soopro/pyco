#coding=utf-8
from __future__ import absolute_import
from plugin_helpers import generate_pagination

_CONFIG = {}
_DEFAULT_PAGINATION_LIMIT  = 10
_term = None
_tax = None
_paged_posts = None
_pagination = None
_TAXONOMY_NAME = "taxonomy"

def config_loaded(config):
    _CONFIG.update(config)
    return
    
def request_url(request, redirect_to):
    global _term
    try:
        _term = request.args.get("term").lower()
    except (ValueError, TypeError, AttributeError):
        _term = None

    global _current_page    
    try:
        _current_page = max(int(request.args.get("paged")), 1)
    except (ValueError, TypeError):
        _current_page = 1
        
    return

def single_post_meta(post_meta, redirect_to):
    global _tax
    _tax = post_meta.get(_TAXONOMY_NAME).lower() if post_meta.get(_TAXONOMY_NAME) else None
    return

def get_post_data(data, post_meta):
    data[_tax] = post_meta.get(_tax).lower() if post_meta.get(_tax) else None
    return
    
def get_posts(posts, current_post, prev_post, next_post):
    global _paged_posts, _pagination
    _paged_posts = _pagination = None
    
    if _term and isinstance(_term, unicode) and _tax:
        tax_posts = []
        for post in posts:
            if post.get(_tax):
                post[_tax] = parseTerms(post[_tax])
            else:
                continue

            if _term in post[_tax]:
                tax_posts.append(post)

        limit = _CONFIG.get("TAXONOMY_PAGINATION_LIMIT", _DEFAULT_PAGINATION_LIMIT )
        _paged_posts, _pagination = generate_pagination(_current_page,limit,tax_posts)
    return

def before_render(var,template):
    var['taxonomy'] = _tax
    if _tax:
        var['results'] = _paged_posts
        var['pagination'] = _pagination
    return

#custom functions
def parseTerms(terms_str):
    terms = []
    if terms_str:
        terms = terms_str.split(',')
        for term in terms:
            term = term.strip().lower()
    return terms