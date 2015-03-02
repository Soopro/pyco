#coding=utf-8
from __future__ import absolute_import
from flask import request, current_app
from itertools import groupby
import math, os, datetime


def plugins_loaded():
    current_app.jinja_env.filters["thumbnail"] = filter_thumbnail
    current_app.jinja_env.filters["type"] = filter_contenttype
    return

def before_render(var, template):
    var["saltshaker"] = saltshaker
    var["stapler"] = stapler
    var["glue"] = glue
    var["barcode"] = barcode
    var["timemachine"] = timemachine
    return


#custom filters
def filter_thumbnail(pic_url):
    try:
        pic_url = str(pic_url)
    except Exception:
        return pic_url

    static_host = current_app.config.get("STATIC_HOST")
    if static_host not in pic_url:
        return pic_url
    
    UPLOAD_DIR = current_app.config.get("UPLOAD_DIR")
    thumbnails_dir = current_app.config.get("THUMBNAILS_DIR")
    THUMB_DIR = os.path.join(UPLOAD_FOLDER,thumbnails_dir)
    new_pic_url = pic_url.replace(UPLOAD_FOLDER,THUMB_FOLDER)
    
    return new_pic_url


def filter_contenttype(raw_pages, ctype=None):
    return salt_shaker(raw_pages,[{"type":ctype}])


#custom functions
def saltshaker(raw_pages, conditions, intersection=False):
    """return a list of result matched conditions.
    result_pages = saltshaker(pages, [{'type':'test'},'thumbnail'],
                  intersection=False)
    """
    results = []
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
    max_pages = int(math.ceil(len(matched_pages)/perpage))

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
    cate_count = barcode(raw_pages, condition="tag")
    """
    ret = dict()
    for page in raw_pages:
        label = page.get(condition)
        if label:
            if label not in ret:
                ret[label] = 1
            else:
                ret[label] += 1
    return ret


def timemachine(raw_pages, filed='date',
                precision='month', time_format='%Y-%m-%d'):
    """return list of pages sort by time.
    sorted_pages = timemachine(raw_pages, filed='date', precision='month',
                               time_format='%Y-%m-%d')
    """
    def parse_datetime(date):
        d = datetime.datetime.strptime(date, time_format)
        if precision == 'year':
            return d.year,
        elif precision == 'month':
            return d.year, d.month
        elif precision == 'day':
            return d.year, d.month, d.day
        elif precision == 'hour':
            return d.year, d.month, d.day, d.hour
        elif precision == 'minute':
            return d.year, d.month, d.day, d.hour, d.minute
        elif precision == 'second':
            return d.year, d.month, d.day, d.hour, d.minute, d.second
        else:
            raise ValueError("arg precision invalid.")

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
