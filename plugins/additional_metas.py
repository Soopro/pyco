#coding=utf-8
from __future__ import absolute_import

_CONFIG = {}
_DEFAULT_ADDITIONAL_METAS = ["nav","link","target","parent","thumbnail"]
_ADDITIONAL_METAS = None
_ORDER_DESC = False
_ORDER_BY = 'date'
_navs = []

def config_loaded(config):
    global _CONFIG, _ADDITIONAL_METAS, _ORDER_BY, _ORDER_DESC

    _CONFIG = config
    
    if _CONFIG.get('PAGE_ORDER') == 'desc':
        _ORDER_DESC = True

    _ORDER_BY = _CONFIG.get('PAGE_ORDER_BY') or _ORDER_BY
    
    _ADDITIONAL_METAS = set(_CONFIG.get("ADDITIONAL_METAS",[]) + _DEFAULT_ADDITIONAL_METAS)
    return


def get_page_data(data, page_meta):
    for key in _ADDITIONAL_METAS:
        data[key] = page_meta.get(key)
    return


def get_pages(pages, current_page, prev_page, next_page):
    # global _navs
 #    _navs = [page for page in pages if page.get("nav")]
 #
 #    for item in _navs:
 #        try:
 #            order = int(item.get('order'))
 #        except Exception:
 #            order = None
 #
 #        item['order'] =  order or 0
 #    _navs=sorted(pages,key=lambda x: (x['order'], x[_ORDER_BY]),reverse=_ORDER_DESC)
    
    return


def before_render(var,template):
    # var["navigation"] = _navs
    return