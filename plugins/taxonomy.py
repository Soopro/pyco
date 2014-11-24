#coding=utf-8
from __future__ import absolute_import
from plugin_helpers import generate_pagination

_CONFIG = {}
_DEFAULT_PAGINATION_LIMIT = 10
_term = None
_tax = None
_paged_pages = None
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


def single_page_meta(page_meta, redirect_to):
    global _tax
    _tax = page_meta.get(_TAXONOMY_NAME).lower() if page_meta.get(_TAXONOMY_NAME) else None
    return


def get_page_data(data, page_meta):
    data[_tax] = page_meta.get(_tax).lower() if page_meta.get(_tax) else None
    return


def get_pages(pages, current_page, prev_page, next_page):
    global _paged_pages, _pagination
    _paged_pages = _pagination = None
    
    if _term and isinstance(_term, unicode) and _tax:
        tax_pages = []
        for page in pages:
            if page.get(_tax):
                page[_tax] = parseTerms(page[_tax])
            else:
                continue

            if _term in page[_tax]:
                tax_pages.append(page)

        limit = _CONFIG.get("TAXONOMY_PAGINATION_LIMIT", _DEFAULT_PAGINATION_LIMIT)
        _paged_pages, _pagination = generate_pagination(_current_page, limit, tax_pages)
    return


def before_render(var, template):
    var['taxonomy'] = _tax
    if _tax:
        var['results'] = _paged_pages
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