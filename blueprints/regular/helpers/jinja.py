# coding=utf-8
from __future__ import absolute_import

from flask import request, g
from itertools import groupby
import os
import datetime

from utils.validators import url_validator
from utils.misc import (sortedby,
                        format_date,
                        get_url_params,
                        add_url_params,
                        make_dotted_dict,
                        match_cond)


# filters
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
    return make_dotted_dict(args)


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
def rope(raw_list, sort_by="updated", priority=True, reverse=False):
    """return a list of sorted results.
    result_pages = rope(pages, sort_by="updated", priority=True, reverse=True)
    """
    sort_keys = _make_sort_keys(sort_by, priority)
    return sortedby(raw_list, sort_keys, reverse)


def magnet(raw_list, current, limit=1):
    curr_idx = None

    for idx, p in enumerate(raw_list):
        p_id = p.get('id')
        if p_id and p_id == current.get('id'):
            curr_idx = idx
            break

    before_list = []
    after_list = []
    if curr_idx is not None:
        before_list = raw_list[max(curr_idx - limit, 0):curr_idx]
        after_list = raw_list[curr_idx + 1:curr_idx + 1 + limit]

    before = before_list[-1] if before_list else None
    after = after_list[0] if after_list else None

    return {
        "before": before,
        "after": after,
        "entries_before": before_list,
        "entries_after": after_list,
    }


def straw(raw_list, value, key='id'):
    """return a item by key/value form a list.
    some_page = straw(pages, some_id, 'id')
    """
    if not isinstance(key, basestring):
        key = 'id'
    try:
        result = [item for item in raw_list if item.get(key) == value][0]
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

    for cond in conditions[:5]:
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
                       if match_cond(i, c_k, c_v, force, opposite)]
        else:
            for i in salts:
                _mch = match_cond(i, cond_key, cond_value, force, opposite)
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


def timemachine(raw_list, filed='date', precision='month',
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

    pages = sorted(filter(lambda x: x.get(filed), raw_list),
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


# other helpers
def _make_sort_keys(sort_by, priority=False):
    sort_keys = [('priority', 1)] if priority else []

    if isinstance(sort_by, basestring):
        sort_keys.append(sort_by)
    elif isinstance(sort_by, list):
        sort_keys = sort_keys + [key for key in sort_by
                                 if isinstance(key, basestring)]
    return sort_keys
