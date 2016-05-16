# coding=utf-8
from __future__ import absolute_import

from flask import request, current_app, g
from itertools import groupby
import math
import os
import datetime

from helpers import sortedby, url_validator, add_url_params

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
    current_app.jinja_env.filters["tostring"] = filter_tostring
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
    var["magnet"] = magnet
    return


# filters
def filter_contenttype(raw_pages, ctype=None, limit=None, sort_by=None):
    if not isinstance(raw_pages, (list, dict)):
        return raw_pages
    result = saltshaker(raw_pages, [{"type": ctype}],
                        limit=limit, sort_by=sort_by)
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
        return os.path.join(g.curr_base_url, url.strip('/'))
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


def filter_tostring(obj):
    if isinstance(obj, basestring):
        return obj
    elif hasattr(obj, '__call__'):
        return ''
    elif obj is None:
        return ''
    else:
        try:
            return str(obj)
        except:
            return ''


# helpers
def rope(raw_pages, sort_by="updated", desc=True, priority=True):
    """return a list of sorted results.
    result_pages = rope(pages, sort_by="updated", desc=True, priority=True)
    """
    sort_keys = []

    if priority:
        sort_keys = ['-priority'] if desc else ['priority']

    if isinstance(sort_by, basestring):
        sort_keys.append(sort_by)
    elif isinstance(sort_by, list):
        sort_keys = sort_keys + [key for key in sort_by
                                 if isinstance(key, basestring)]

    return sortedby(raw_pages, sort_keys, desc)


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


def saltshaker(raw_salts, conditions, limit=None,
               intersection=True, sort_by=None):
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
        for k, v in raw_salts.iteritems():
            v['_saltkey'] = k
            salts.append(v)
    else:
        salts = raw_salts

    def _match_cond(cond_value, cond_key, target,
                    opposite=False, force=False):
        if cond_value == '' and not force:
            return _deep_in(cond_key, target) != opposite
        elif cond_value is None and not force:
            # if cond_value is None will reverse the opposite,
            # then for the macthed opposite must reverse again. so...
            # alaso supported if the target value really is None.
            return _deep_in(cond_key, target) == opposite
        elif isinstance(cond_value, bool) and not force:
            return _deep_in(cond_key, target) != opposite
        elif not _deep_in(cond_key, target):
            return False

        matched = False
        target_value = _deep_get(cond_key, target)
        if isinstance(cond_value, list):
            for cv in cond_value:
                matched = _match_cond(cv, target_value, force=True)
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

    for cond in conditions:
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
            results = [
                i for i in results
                if _match_cond(cond_value, cond_key, i, opposite, force)
            ]
        else:
            for i in salts:
                if i not in results and \
                        _match_cond(cond_value, cond_key, i, opposite, force):
                    results.append(i)

    # sort by
    if sort_by and hasattr(rope, '__call__'):
        results = rope(results, sort_by)

    # limit
    if limit > 0:
        results = results[0:limit]
        # do not limit in loop, because results is not settled down.
    return results


def glue(args=None, url=None):
    """return a url with added args.
    relative_path_args = glue(\{"key": "value"\})
    """
    if not url:
        url = g.request_url or request.url
    return add_url_params(url, args)


def stapler(raw_pages, paged=1, perpage=12):
    """return dict for paginator.
    booklet = stapler(pages, paged=1, perpage=12)
    """
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
            raise ValueError("invalid date format. \
                              It should be str, unicode, \
                              timestamp(int) or datetime object")
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
                    'slug': p.get('slug'),
                    'url': p.get('url'),
                }
                break
            elif p.get('id') and p.get('id') == pid:
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
def _deep_get(key, obj):
    if not isinstance(obj, dict):
        return None
    if '.' not in key:
        return obj.get(key)
    else:
        _key_pairs = key.split('.', 1)
        _obj = obj.get(_key_pairs[0])
        _value = _deep_get(_key_pairs[1], _obj)
        return _value


def _deep_in(key, obj):
    if not isinstance(obj, dict):
        return False
    if '.' not in key:
        return key in obj
    else:
        _key_pairs = key.split('.', 1)
        _obj = obj.get(_key_pairs[0])
        _in = _deep_in(_key_pairs[1], _obj)
        return _in
