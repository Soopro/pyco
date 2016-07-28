# coding=utf-8
from __future__ import absolute_import

from flask import request, current_app, g
from itertools import groupby
import math
import os
import datetime

from helpers import (parse_int,
                     sortedby,
                     url_validator,
                     format_date,
                     get_url_params,
                     add_url_params,
                     DottedImmutableDict)


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
    current_app.jinja_env.filters["args"] = filter_args
    current_app.jinja_env.filters["date_formatted"] = filter_date_formatted
    return


def before_render(var, template):
    if not template:
        return
    var["saltshaker"] = saltshaker
    var["stapler"] = stapler
    var["straw"] = straw
    var["rope"] = rope
    var["glue"] = glue
    var["barcode"] = barcode
    var["timemachine"] = timemachine
    var["gutter"] = gutter
    var["magnet"] = magnet
    return


# filters
def filter_contenttype(raw_pages, ctype=None, limit=None, sort_by=None):
    if not isinstance(raw_pages, (list, dict)):
        return raw_pages
    if hasattr(saltshaker, '__call__'):
        result = saltshaker(raw_pages, [{"type": ctype}],
                            limit=limit, sort_by=sort_by)
    else:
        result = []
    return result


def filter_thumbnail(pic_url, suffix='thumbnail'):
    allowed_exts = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff']
    try:
        _ext = os.path.splitext(pic_url)[1][1:].lower()
    except:
        _ext = None

    if pic_url.startswith(g.uploads_url) and _ext in allowed_exts:
        pair = '&' if '?' in pic_url else '?'
        pic_url = "{}{}{}".format(pic_url, pair, suffix)

    return pic_url


def filter_url(url, remove_args=False, remove_hash=False):
    if not isinstance(url, basestring):
        return url
    if remove_args:
        url = url.split("?")[0]
    if remove_hash:
        url = url.split("#")[0]
    if not url or url_validator(url):
        return url
    elif url.startswith('/'):
        return "{}/{}".format(g.curr_base_url, url.strip('/'))
    else:
        return url.rstrip('/')


def filter_path(url, remove_args=True, remove_hash=True):
    if not isinstance(url, basestring):
        return url
    if remove_args:
        url = url.split("?")[0]
    if remove_hash:
        url = url.split("#")[0]
    try:
        path = url.split(g.curr_base_url)[-1]
    except:
        path = url

    return "/{}".format(path.strip('/'))


def filter_args(url, unique=True):
    if not isinstance(url, basestring):
        args = {}
    else:
        args = get_url_params(url, unique)
    return DottedImmutableDict(args)


def filter_date_formatted(date, to_format=None):
    if not date:
        return ''
    if not isinstance(to_format, basestring):
        to_format = None

    formats = {
        "en": u'%B %d, %Y',
        "zh": u'%Y年 %m月 %d日',
    }

    try:
        locale = g.curr_app["locale"]
        lang = locale.split('_')[0]
    except:
        locale = None
        lang = None

    to_format = to_format or formats.get(locale) or formats.get(lang)
    return format_date(date, to_format)


# jinja helpers
def rope(raw_pages, sort_by="updated", priority=True, reverse=True):
    """return a list of sorted results.
    result_pages = rope(pages, sort_by="updated", priority=True, reverse=True)
    """
    sort_keys = _make_sort_keys(sort_by, priority, reverse)
    return sortedby(raw_pages, sort_keys, reverse)


def magnet(raw_pages, current, limit=1):
    before_pages = []
    after_pages = []
    curr_idx = None
    for idx, p in enumerate(raw_pages):
        p_id = p.get('id')
        if p_id and p_id == current.get('id'):
            curr_idx = idx
            break

    if curr_idx is not None:
        before_pages = raw_pages[:curr_idx][-limit:]
        after_pages = raw_pages[curr_idx:][1:][:limit]

    return {
        "before": before_pages or [None],
        "after": after_pages or [None]
    }


def straw(raw_list, value, key='id'):
    """return a item by key/value form a list.
    next_page = straw(pages, next_id, 'id')
    """
    if not isinstance(key, basestring):
        key = 'id'
    try:
        result = [item for item in raw_list
                  if _deep_get(key, item) == value][0]
    except:
        result = None
    return result


def saltshaker(raw_salts, conditions, limit=None, sort_by=None,
               intersection=True):
    """return a list of results matched conditions.
    result_pages = saltshaker(pages, [{'type':'test'},'thumbnail'],
                              limit=12, intersection=True, sort_by='updated')
    """

    if not isinstance(raw_salts, (list, dict)):
        return []
    elif isinstance(raw_salts, dict):
        salts = []
        for k, v in raw_salts.iteritems():
            v['_saltkey'] = k
            salts.append(v)
    else:
        salts = raw_salts

    if not isinstance(conditions, list):
        conditions = [conditions]

    results = []

    for cond in conditions[:10]:
        opposite = False
        force = False
        cond_key = None
        cond_value = ''
        if isinstance(cond, (str, unicode)):
            cond_key = cond.lower()
        elif isinstance(cond, dict):
            opposite = bool(cond.pop('not', False))
            force = bool(cond.pop('force', False))
            if cond:
                cond_key = cond.keys()[0]
                cond_value = cond[cond_key]
            else:
                continue

        if cond_key is None:
            continue

        if intersection and results:
            c_k = cond_key
            c_v = cond_value
            results = [i for i in results
                       if _match_cond(i, c_k, c_v, opposite, force)]
        else:
            for i in salts:
                _mch = _match_cond(i, cond_key, cond_value, opposite, force)
                if i not in results and _mch:
                    results.append(i)
    # sort by
    if sort_by:
        sort_keys = _make_sort_keys(sort_by)
        results = sortedby(results, sort_keys)

    # limit
    if limit > 0:
        results = results[0:limit]
        # do not limit in loop, because results is not settled down.
    return results


def glue(args=None, url=None, unique=True):
    """return a url with added args.
    relative_path_args = glue(\{"key": "value"\})
    """
    if not url:
        url = g.request_url or request.url
    return add_url_params(url, args, unique=unique)


def stapler(raw_pages, paged=1, perpage=12):
    """return dict for paginator.
    booklet = stapler(pages, paged=1, perpage=12)
    """
    perpage = parse_int(perpage, 12, True)
    paged = parse_int(paged, 1, True)

    matched_pages = raw_pages
    max_pages = int(math.ceil(len(matched_pages) / float(perpage)))

    max_pages = max(max_pages, 1)
    paged = min(max_pages, paged)

    start = (paged - 1) * perpage
    end = paged * perpage
    result_pages = matched_pages[start:end]

    return {
        "pages": result_pages,
        "max": max_pages,
        "paged": paged
    }


def barcode(raw_pages, field="taxonomy.category", sort=True, desc=True):
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
        term = _deep_get(field, page)
        if isinstance(term, (list, dict)):
            obj = term if isinstance(term, dict) else xrange(len(term))
            for i in obj:
                if not isinstance(term[i], basestring):
                    continue
                count(term[i])
        else:
            count(term)

    bars = []
    for k, v in ret.iteritems():
        bars.append({"key": k, "count": v})

    if sort:
        bars = sortedby(bars, "count", desc)

    return bars


def timemachine(raw_pages, filed='date', precision='month',
                time_format='%Y-%m-%d', reverse=True):
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
        if isinstance(date, basestring):
            date = datetime.datetime.strptime(date, time_format)
        elif isinstance(date, int):
            date = datetime.datetime.fromtimestamp(date)
        elif isinstance(date, datetime.datetime):
            date = date
        else:
            raise ValueError("invalid date format.")
        try:
            return get_group_key.get(precision, 'month')(date)
        except Exception:
            raise ValueError("invalid precision, precision must be str.")

    pages = sorted(filter(lambda x: x.get(filed), raw_pages),
                   key=lambda x: x[filed],
                   reverse=reverse)

    # iterator version
    # return groupby(pages, key=lambda x: parse_datetime(x.get('date')))

    # list version
    ret = []
    raw_group = groupby(pages, key=lambda x: parse_datetime(x.get(filed)))
    for date, group in raw_group:
        ret.append((date, [x for x in group]))

    return ret


def gutter(page_id, structures):
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
                    'slug': p.get('slug'),
                    'url': p.get('url'),
                }
                break
            elif p.get('id') and p.get('id') == page_id:
                curr_page = p
            else:
                prev_page = {
                    'id': p.get('id'),
                    'title': p.get('title'),
                    'slug': p.get('slug'),
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


# other helpers
def _match_cond(target, cond_key, cond_value, opposite=False, force=False):
    """
    params:
    - target: the source data want to check.
    - cond_key: the attr key of condition.
    - cond_value: the value of condition.
      if the cond_value is a list, any item matched will make output matched.
    - opposite: reverse check result.
    - force: must have the value or not.
    """
    if cond_value == '' and not force:
        return _deep_in(cond_key, target) != opposite
    elif cond_value is None and not force:
        # if cond_value is None will reverse the opposite,
        # then for the macthed opposite must reverse again. so...
        # also supported if the target value really is None.
        return _deep_in(cond_key, target) == opposite
    elif isinstance(cond_value, bool) and not force:
        return _deep_in(cond_key, target) != opposite
    elif not _deep_in(cond_key, target):
        return False

    matched = False
    target_value = _deep_get(cond_key, target)
    if isinstance(cond_value, list):
        for c_val in cond_value:
            matched = _match_cond(target, cond_key, c_val, force=True)
            if matched:
                break
    elif isinstance(cond_value, bool):
        target_bool = isinstance(target_value, bool)
        matched = cond_value == target_value and target_bool
    else:
        if isinstance(target_value, list):
            matched = cond_value in target_value
        else:
            matched = cond_value == target_value

    return matched != opposite


def _make_sort_keys(sort_by, priority=False, reverse=False):
    sort_keys = []

    if priority:
        sort_keys = ['-priority'] if reverse else ['priority']

    if isinstance(sort_by, basestring):
        sort_keys.append(sort_by)
    elif isinstance(sort_by, list):
        sort_keys = sort_keys + [key for key in sort_by
                                 if isinstance(key, basestring)]
    return sort_keys


def _deep_get(key, obj):
    if not isinstance(obj, dict):
        return None
    elif '.' not in key:
        return obj.get(key)
    else:
        key_pairs = key.split('.', 1)
        obj = obj.get(key_pairs[0])
        return _deep_get(key_pairs[1], obj)


def _deep_in(key, obj):
    if not isinstance(obj, dict):
        return False
    elif '.' not in key:
        return key in obj
    else:
        key_pairs = key.split('.', 1)
        obj = obj.get(key_pairs[0])
        return _deep_in(key_pairs[1], obj)
