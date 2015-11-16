#coding=utf-8
from __future__ import absolute_import

from flask import request, current_app, g
from itertools import groupby
import math, os, datetime, re

from helpers import sortby, url_validator

ERROR_EXCESSIVE = "Excessive"
_CONFIG = {}

def config_loaded(config):
    global _CONFIG
    _CONFIG = config
    return

def plugins_loaded():
    current_app.jinja_env.filters["thumbnail"] = filter_thumbnail
    current_app.jinja_env.filters["type"] = filter_contenttype
    current_app.jinja_env.filters["url"] = filter_url
    current_app.jinja_env.filters["path"] = filter_path
    return

def before_render(var, template):
    var["saltshaker"] = saltshaker
    var["stapler"] = stapler
    var["straw"] = straw
    var["rope"] = rope
    var["glue"] = glue
    var["barcode"] = barcode
    var["timemachine"] = timemachine
    var["gutter"] = gutter
    return


#custom filters
def filter_contenttype(raw_pages, ctype = None, limit = None, sort_by = None):
    if not isinstance(raw_pages, (list, dict)):
        return raw_pages
    return saltshaker(raw_pages, [{"type": ctype}], 
                                 limit = limit, sort_by = sort_by)
                      
def filter_thumbnail(pic_url):
    if not isinstance(pic_url, (str, unicode)):
        return pic_url
    
    if g.static_host not in pic_url:
        return pic_url
    
    uploads_dir = "uploads"
    thumb_dir = os.path.join(uploads_dir, "thumbnails")
    
    pattern = "/{}/".format(uploads_dir)
    replacement = "/{}/".format(thumb_dir)
    new_pic_url = pic_url.replace(pattern, replacement, 1)
    
    return new_pic_url


def filter_url(url, remove_args=False):
    if not isinstance(url,(str, unicode)):
        return url
    if remove_args:
        url = url.split("?")[0]
    if not url or url_validator(url):
        return url
    elif url.startswith('/'):
        return os.path.join(g.curr_base_url, url.strip('/'))
    else:
        url.rstrip('/')


def filter_path(url, remove_args = True):
    if not isinstance(url, (str, unicode)):
        return url
    if remove_args:
        url = url.split("?")[0]
    try:
        path = url.split(g.curr_base_url)[-1]
    except:
        path = url
    return path.strip('/')



#custom functions
def rope(raw_pages, sort_by = "updated", desc = True, priority = True):
    """return a list of sorted results.
    result_pages = rope(pages, sort_by="updated", desc=True, priority=True)
    """
    sort_keys = []

    if priority:
        sort_keys = ['-priority'] if desc else ['priority']
        
    if isinstance(sort_by, (str, unicode)):
        sort_keys.append(sort_by)
    elif isinstance(sort_by, list):
        sort_keys = sort_keys + [key for key in sort_by 
                                 if isinstance(key, (str, unicode))]
    
    return sortby(raw_pages, sort_keys, desc)


def straw(raw_list, value, key = 'id'):
    """return a item by key/value form a list.
    next_page = straw(pages, next_id, 'id')
    """
    if not isinstance(key, (str, unicode)):
        key = 'id'
    try:
        result = [item for item in raw_list if item.get(key) == value][0]
    except:
        result = None
    return result


def saltshaker(raw_salts, conditions, limit = None, 
                          intersection = True, sort_by = None):
    """return a list of results matched conditions.
    result_pages = saltshaker(pages, [{'type':'test'},'thumbnail'],
                              limit=12, intersection=True, sort_by='updated')
    """
    results = []
    try:
        limit = int(limit)
    except:
        limit = 0
    
    if not isinstance(raw_salts, (list, dict)):
        return ERROR_EXCESSIVE

    if not isinstance(conditions, list):
        conditions = [conditions]
    
    # process if raw salts is dict
    if isinstance(raw_salts, dict):
        salts = []
        for k,v in raw_salts.iteritems():
            v['_saltkey'] = k
            salts.append(v)
    else:
        salts = raw_salts
    
    
    def match_cond(cond_value, target_value, opposite=False):
        if cond_value == None:
            return True
        
        if isinstance(cond_value, list):
            for cv in cond_value:
                matched = match_cond(cv, target_value)
                if matched:
                    break
        elif isinstance(cond_value, bool):
            matched = cond_value == bool(target_value)
        else:
            if isinstance(target_value, list):
                matched = cond_value in target_value
            else:
                matched = cond_value == target_value

        return matched != opposite
        
        

    for cond in conditions:
        opposite = False
        if isinstance(cond, (str, unicode)):
            cond_key = cond.lower()
            cond_value = None
        elif isinstance(cond, dict):
            opposite = bool(cond.pop('not', False))
            
            if cond:
                cond_key = cond.keys()[0]
                cond_value = cond[cond_key]
            else:
                continue
            
        if intersection and results:
            results = [i for i in results if cond_key in i
                       and match_cond(cond_value, i.get(cond_key), opposite)]
        else:
            for i in salts:
                if cond_key in i and i not in results \
                and match_cond(cond_value, i.get(cond_key), opposite):
                    results.append(i)

    # sort by
    if sort_by and hasattr(rope, '__call__'):
        results = rope(results, sort_by, True)
    
    # limit
    if limit > 0:
        results = results[0:limit]
        # do not limit in loop, because results is not settled down.
    return results


def glue(args = None, url = None):
    """return a url with added args.
    relative_path_args = glue(args)
    """
    argments = {k:v for k,v in request.args.items()}
    if not url:
        try:
            _path = g.request_path or request.path
        except:
            _path = request.path
        
        url = os.path.join(g.curr_base_url, _path.lstrip('/'))
    if isinstance(args, dict):
        argments.update(args)

    conn_symbol = "?"
    if conn_symbol in url:
        conn_symbol = "&"
    
    new_args = "&".join(['%s=%s' % (key, value) 
                    for (key, value) in argments.items()])

    url="{}{}{}".format(url, conn_symbol, new_args)
    return url


def stapler(raw_pages, paged = 1, perpage = 12):
    """return dict for paginator.
    booklet = stapler(pages, paged=1, perpage=12)
    """
    matched_pages = raw_pages
    max_pages = int(math.ceil(len(matched_pages)/float(perpage)))

    max_pages = max(max_pages, 1)
    paged = min(max_pages, paged)

    start = (paged-1)*perpage
    end = paged*perpage
    result_pages = matched_pages[start:end]

    return {
        "pages": result_pages,
        "max": max_pages,
        "paged": paged
    }


def barcode(raw_pages, field = "category", sort = True, desc = True):
    """return dict count entries has same value of specified field.
    count = barcode(pages, field="category", sort=True, desc=True)
    """
    ret = dict()
    def count(term):
        if term:
            if term not in ret:
                ret[term] = 1
            else:
                ret[term] += 1

    for page in raw_pages:
        term = page.get(field)
        if isinstance(term, (list, dict)):
            obj = term if isinstance(term, dict) else xrange(len(term))
            for i in obj:
                if not isinstance(term[i], (str, unicode)):
                    continue
                count(term[i])
        else:
            count(term)
    
    bars = []
    for k,v in ret.iteritems():
        bars.append({"key":k, "count": v})
    
    if sort:
        bars = sortby(bars, "count", desc)
    
    return bars


def timemachine(raw_pages, filed = 'date', precision = 'month',
                time_format = '%Y-%m-%d', reverse = True):
    """return list of pages grouped by datetime.
    sorted_pages = timemachine(pages, filed='date', precision='month',
                               time_format='%Y-%m-%d',reverse=True)
    """
    get_group_key = {
        'year': lambda x: x.year,
        'month': lambda x: (x.year, x.month),
        'day': lambda x: (x.year, x.month, x.day),
        'hour': lambda x: (x.month, x.day, x.hour, x.minute),
        'minute': lambda x: (x.month, x.day, x.hour, x.minute),
        'second': lambda x: (x.month, x.day, x.hour, x.minute, x.second)
    }
    
    def parse_datetime(date):
        if isinstance(date, (str, unicode)):
            date = datetime.datetime.strptime(date, time_format)
        elif isinstance(date, int):
            date = datetime.datetime.fromtimestamp(date)
        elif isinstance(date, datetime.datetime):
            date = date
        else:
            raise ValueError("invalid date format. \
                              It should be str, unicode, \
                              timestamp(int) or datetime object")
        try:
            return get_group_key.get(precision, 'month')(date)
        except Exception:
            raise ValueError("invalid precision, precision must be str.")


    pages = sorted(filter(lambda x: x.get(filed), raw_pages),
                   key = lambda x: x[filed], 
                   reverse = reverse)

    # iterator version
    # return groupby(pages, key=lambda x: parse_datetime(x.get('date')))

    # list version
    ret = []
    raw_group = groupby(pages, key=lambda x: parse_datetime(x.get(filed)))
    for date, group in raw_group:
        ret.append((date, [x for x in group]))

    return ret
    

# def gutter(raw_pages, structures):
#     """return a list of grouped pages by structures.
#     bookpages = gutter(pages, menu.gutter.nodes)
#     tip: the second param is list contain structure, must be a 2 level menu.
#     etc., 'chapter' host 'pages', use 'page.id' to relate with source pages.
#     """
#
#     if not isinstance(structures, list) or not isinstance(raw_pages, list):
#         return ERROR_EXCESSIVE
#
#     def _find_source(ref, source):
#         try:
#             for f in source:
#                 if f.get('id') and f.get('id') == ref.get('id'):
#                     return f
#             return None
#         except:
#             return None
#
#     results = []
#     for struct in structures:
#         group = {
#             'alias': struct.get('alias'),
#             'title': struct.get('title'),
#             'meta': struct.get('meta'),
#             'pages': struct.get('nodes'),
#         }
#         pages = group['pages']
#         badlist = []
#         for i, p in enumerate(pages):
#             page = _find_source(p, raw_pages)
#             if not p or not page:
#                 badlist.append(i)
#                 continue
#             p.update(page)
#
#         for idx in reversed(badlist):
#             pages.pop(idx)
#
#         results.append(group)
#
#     return results

def gutter(pid, structures):
    """return a dict of next/prev page by structures.
    page_gutter = gutter(meta.id, menu.gutter.nodes)
    """
    next_page = None
    prev_page = None
    curr_page = None
    for struct in structures:
        for p in struct.get('nodes', []):
            if curr_page is not None:
                next_page = {
                    'id': p.get('id'),
                    'title': p.get('title'),
                    'alias': p.get('alias'),
                    'url': p.get('url'),
                }
                break
            elif p.get('id') and p.get('id') == pid:
                curr_page = p
            else:
                prev_page = {
                    'id': p.get('id'),
                    'title': p.get('title'),
                    'alias': p.get('alias'),
                    'url': p.get('url'),
                }
        if next_page is not None:
            break

    if not curr_page:
        next_page = prev_page = None

    return {
        'prev_page': prev_page,
        'next_page': next_page
    }