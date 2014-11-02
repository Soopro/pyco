#coding=utf-8
from __future__ import absolute_import

_CONFIG = {}
_ORDER_DESC = False
_ORDER_BY = 'date'
_PRIORITY = 'priority'

def config_loaded(config):
    global _CONFIG, _ORDER_DESC, _ORDER_BY

    _CONFIG = config

    if _CONFIG.get('PAGE_ORDER') == 'desc':
        _ORDER_DESC = True

    _ORDER_BY = _CONFIG.get('PAGE_ORDER_BY') or _ORDER_BY
    return

def get_page_data(data, page_meta):
    data[_PRIORITY] = page_meta.get(_PRIORITY)
    return

def get_pages(pages, current_page, prev_page, next_page):
    for page in pages:
        try: 
            order = int(page.get(_PRIORITY))
        except Exception:
            order = None

        page[_PRIORITY] =  order or 0
    _pages=sorted(pages,key=lambda x: (x[_PRIORITY], x[_ORDER_BY]),reverse=_ORDER_DESC)
    
    del pages[:]
    for page in _pages:
        pages.append(page)
    return