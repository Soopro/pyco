#coding=utf-8
from __future__ import absolute_import
from flask import request, current_app
from itertools import groupby
import math, os, datetime, re

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


def filter_contenttype(raw_pages, ctype=None, limit=None, sortby=None):
    if not isinstance(raw_pages, (list, dict)):
        return raw_pages
    return saltshaker(raw_pages, [{"type": ctype}], limit=limit, sortby=sortby)


def filter_url(url, remove_args=False):
    if not isinstance(url,(str, unicode)):
        return url
    if remove_args:
        url = url.split("?")[0]
    if re.match("^(?:http|ftp)s?://", url):
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
def rope(pages, sortby, desc=True, priority=True):
    if not isinstance(pages, list) or not isinstance(sortby, (str, unicode)):
        return pages
        
    sort_desc = desc
    
    if sortby[0:1] == '-':
        sort_desc = False
        sort_key = sortby[1:]
    elif sortby[0:1] == '+':
        sort_key = sortby[1:]
    
    if not sort_key:
        sort_key = 'updated'
        
    if not priority:
        return sorted(pages, key=lambda x:x[sort_key],
                      reverse=sort_desc)
    else:
        return sorted(pages, key=lambda x: (x['priority'], x[sort_key]),
                      reverse=sort_desc)

def saltshaker(raw_pages, conditions, intersection=False, 
               limit=None, sortby=None):
    """return a list of result matched conditions.
    result_pages = saltshaker(pages, [{'type':'test'},'thumbnail'],
                              intersection=False, limit=12, sortby='updated')
    """
    results = []
    try:
        limit = int(limit)
    except:
        limit = 0

    obj = raw_pages
    if not isinstance(conditions, list) or len(conditions) > 10 \
    and not isinstance(obj, (list,dict)):
        return "Excessive"

    for cond in conditions:
        if isinstance(cond, (str,unicode)):
            cond_key = cond.lower()
            cond_value = None
        elif isinstance(cond, dict):
            cond_key = cond.keys()[0]
            cond_value = cond[cond_key]

        if isinstance(obj, dict) and not results:
            new_items = {k: v for (k, v) in obj.iteritems()
                        if k == cond_key and v 
                        and (cond_value == None or cond_value == v)}
            results.append(new_items)
            continue

        if intersection and results:
            results = [i for i in results if i.get(cond_key)
                        and (cond_value == i.get(cond_key)
                           or cond_value == None)]
        else:
            for i in obj:
                if i.get(cond_key) and i not in results \
                and (cond_value == None or cond_value == i.get(cond_key)):
                    results.append(i)
    # sortby
    if sortby:
        results = rope(results, sortby)
    
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
                time_format='%Y-%m-%d'):
    """return list of pages sort by time.
    sorted_pages = timemachine(raw_pages, filed='date', precision='month',
                               time_format='%Y-%m-%d')
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
                   key=lambda x: x[filed], 
                   reverse=True)

    # iterator version
    # return groupby(pages, key=lambda x: parse_datetime(x.get('date')))

    # list version
    ret = []
    raw_group = groupby(pages, key=lambda x: parse_datetime(x.get(filed)))
    for date, group in raw_group:
        ret.append((date, [x for x in group]))
    return ret
