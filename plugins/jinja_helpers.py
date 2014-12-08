#coding=utf-8
from __future__ import absolute_import
from flask import request
import math


def before_render(var, template):
    var["saltshaker"] = salt_shaker
    var["stapler"] = stapler
    var["glue"] = glue
    var["barcode_scanner"] = barcode_scanner
    var["sort_by_date"] = sort_by_date
    return


#custom functions
def salt_shaker(raw_pages, conditions, intersection=False):
    #return a list of result matched conditions.
    #result_pages = salt_shaker(pages, [{'type':'test'},'thumbnail'],
    #               intersection=False)

    results = []
    obj = raw_pages
    if not isinstance(conditions, list) or len(conditions) > 10 \
    and not isinstance(obj, (list,dict)):
        return "Excessive"

    for cond in conditions:
        if isinstance(cond, str):
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


def glue(args=None):
    #return a path + args, but not domain.
    #relative_path_args = glue(args)
    argments = {k: v for k, v in request.args.items()}
    if isinstance(args, dict):
        argments.update(args)
    url = request.path+"?"+"&".join(
                ['%s=%s' % (key, value) for (key, value) in argments.items()])
    return url


def stapler(raw_pages, paged=1, perpage=12):
    #return dict for paginator.
    #booklet = stapler(pages, paged=1, perpage=12)
    matched_pages = raw_pages
    max_pages = int(math.ceil(len(matched_pages)/perpage))

    max_pages = max(max_pages, 1)
    paged = min(max_pages, paged)

    start = (paged-1)*perpage
    end = paged*perpage
    result_pages = matched_pages[start:end]
    
    return {"pages": result_pages,
            "max": max_pages,
            "paged": paged}


def barcode_scanner(raw_pages, condition="category"):
    #return dict with category alias and count.
    #cate_count = barcode_scanner(raw_pages, condition="tag")
    ret = dict()
    for page in raw_pages:
        label = page.get(condition)
        if label:
            if label not in ret:
                ret[label] = 1
            else:
                ret[label] += 1
    return ret


def sort_by_date(raw_pages, key='date', reverse=True):
    return sorted(raw_pages, key=lambda x: (x.get(key)), reverse=reverse)
