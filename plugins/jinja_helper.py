#coding=utf-8
from __future__ import absolute_import

from flask import request, current_app
from itertools import groupby
import math, os, datetime, re

from helpers import sortby, url_validator


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
    var["rope"] = rope
    var["glue"] = glue
    var["barcode"] = barcode
    var["timemachine"] = timemachine
    return


#custom filters
def filter_thumbnail(pic_url):

    if not isinstance(pic_url, (str, unicode)):
        return pic_url

    base_url = _CONFIG.get("BASE_URL")
    uploads_dir = _CONFIG.get("UPLOADS_DIR")
    uploads_path = os.path.join(base_url, uploads_dir)
    if uploads_path not in pic_url:
        return pic_url
    
    thumb_dir = os.path.join(uploads_dir, _CONFIG.get("THUMBNAILS_DIR"))

    pattern = "/{}/".format(uploads_dir)
    replacement = "/{}/".format(thumb_dir)
    new_pic_url = pic_url.replace(pattern, replacement)
    
    return new_pic_url


def filter_contenttype(raw_pages, ctype=None, limit=None, sort_by=None):
    if not isinstance(raw_pages, (list, dict)):
        return raw_pages
    return saltshaker(raw_pages, [{"type": ctype}], limit=limit,
                      sort_by=sort_by)


def filter_url(url, remove_args=False):
    if not isinstance(url,(str, unicode)):
        return url
    if remove_args:
        url = url.split("?")[0]
    if url_validator(url):
        return url
    else:
        base_url = os.path.join(_CONFIG.get("BASE_URL"), '')
        return os.path.join(base_url, url.strip('/'))

def filter_path(url, remove_args=True):
    if not isinstance(url,(str,unicode)):
        return url
    if remove_args:
        url = url.split("?")[0]
    base_url = os.path.join(_CONFIG.get("BASE_URL"), '')
    url = url.split(base_url)[-1]
    url = url.strip('/')
    return "/{}".format(url)


#custom functions
def rope(pages, sort_by, desc=True, priority=True):
    sort_desc = desc
    sort_keys = []
    
    if priority:
        sort_keys = ['priority']
    
    if isinstance(sort_by, (str, unicode)):
        sort_keys.append(sort_by)
    elif isinstance(sort_by, list):
        sort_keys = sort_keys + [key for key in sort_by 
                                 if isinstance(key, (str, unicode))]
    
    return sortby(pages, sort_keys, desc)


def saltshaker(raw_salts, conditions, limit= None, 
                          intersection = True, sort_by= None):

    """return a list of result matched conditions.
    result_pages = saltshaker(pages, [{'type':'test'},'thumbnail'], limit=12,
                                      intersection=False, sort_by='updated')
    """
    results = []
    try:
        limit = int(limit)
    except:
        limit = 0
    
    if not isinstance(conditions, list) \
    and not isinstance(raw_salts, (list, dict)):
        return "Excessive"
    
    # process if raw salts is dict
    if isinstance(raw_salts, dict):
        salts = []
        for k,v in raw_salts.iteritems():
            v['_saltkey'] = k
            salts.append(v)
    else:
        salts = raw_salts
    
    
    def match_cond(cond_value, target_value):
        if cond_value == None:
            return True
        elif isinstance(cond_value, bool):
            return cond_value == bool(target_value)
        else:
            return cond_value == target_value

    for cond in conditions:
        if isinstance(cond, (str, unicode)):
            cond_key = cond.lower()
            cond_value = None
        elif isinstance(cond, dict):
            cond_key = cond.keys()[0]
            cond_value = cond[cond_key]
        

        if intersection and results:
            results = [i for i in results if cond_key in i
                       and match_cond(cond_value, i.get(cond_key))]
        else:
            for i in salts:
                if cond_key in i and i not in results \
                and match_cond(cond_value, i.get(cond_key)):
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
    """return a path + args, but not domain.
    relative_path_args = glue(args)
    """
    argments = {k:v for k,v in request.args.items()}
    if not url:
        url = request.path
    if isinstance(args, dict):
        argments.update(args)

    conn_symbol = "?"
    if conn_symbol in url:
        conn_symbol = "&"
    
    new_args = "&".join(['%s=%s' % (key, value) 
                    for (key, value) in argments.items()])

    url="{}{}{}".format(url, conn_symbol, new_args)
    return url


def stapler(raw_pages, paged=1, perpage=12):
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


def barcode(raw_pages, condition="category"):
    """return dict with category alias and count.
    cate_count = barcode(raw_pages, condition="tags")
    """
    ret = dict()
    def count(term):
        if term:
            if term not in ret:
                ret[term] = 1
            else:
                ret[term] += 1

    for page in raw_pages:
        term = page.get(condition)
        if isinstance(term, (list, dict)):
            obj = term if isinstance(term, dict) else xrange(len(term))
            for i in obj:
                count(term[i])
        else:
            count(term)
    return ret


def timemachine(raw_pages, filed='date', precision='month',
                time_format='%Y-%m-%d', reverse=True):
    """return list of pages sort by time.
    sorted_pages = timemachine(raw_pages, filed='date', precision='month',
                               time_format='%Y-%m-%d',reverse=True)
    """
    def parse_datetime(date):
        if isinstance(date, str):
            date = datetime.datetime.strptime(date, time_format)
        elif isinstance(date, int):
            date = datetime.datetime.fromtimestamp(date)
        elif isinstance(date, datetime):
            date = date
        else:
            raise ValueError("invalid date format.It should be str, \
                              timestamp(int) or datetime object")

        get_group_key = {
            'year': lambda x: x.year,
            'month': lambda x: (x.year, x.month),
            'day': lambda x: (x.year, x.month, x.day),
            'hour': lambda x: (x.month, x.day, x.hour, x.minute),
            'minute': lambda x: (x.month, x.day, x.hour, x.minute),
            'second': lambda x: (x.month, x.day, x.hour, x.minute, x.second)
        }

        try:
            return get_group_key[precision](date)
        except Exception:
            raise ValueError("invalid precision, precision must be 'year', \
                              'month' or 'day'.")


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