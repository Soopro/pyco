#coding=utf-8
from __future__ import absolute_import
from flask import request
import math


def before_render(var, template):
    var["saltshaker"] = salt_shaker
    var["stapler"] = stapler
    var["glue"] = glue
    var["barcode_scanner"] = barcode_scanner
    return


#custom functions
def salt_shaker(raw_pages, conditions, intersection=False):
    results = []
    obj = raw_pages
    if not isinstance(conditions, list) or len(conditions) > 10:
        return "Excessive"

    for cond in conditions:
        if isinstance(cond, str):
            cond_key = cond.lower()
            cond_value = None
        elif isinstance(cond, dict):
            cond_key = cond.keys()[0]
            cond_value = cond.get(cond_key)

        if isinstance(obj, list):            
            if intersection and results:
                results = [i for i in results if i.get(cond_key) and (cond_value is None or cond_value == i.get(cond_key))]
            else:
                for i in obj:
                    if i.get(cond_key) and i not in results and (cond_value is None or cond_value == i.get(cond_key)):
                        results.append(i)

        elif isinstance(obj, dict):
            if intersection and results:
                new_items = {k: v for (k, v) in results
                            if k == cond_key and v 
                            and (cond_value == None or cond_value == v)}

                results.append(new_items)

            else:
                new_items = {k: v for (k, v) in obj.iteritems() 
                            if k == cond_key and v 
                            and (cond_value == None or cond_value == v)}

                results.append(new_items)
    # for i in results:
    #     print i.get('type')
    return results


def glue(args=None):
    argments = {k: v for k, v in request.args.items()}
    if isinstance(args, dict):
        argments.update(args)
    url = request.path+"?"+"&".join(['%s=%s' % (key, value) for (key, value) in argments.items()])
    return url


def stapler(raw_pages, paged=1, perpage=12, content_types=None):
    matched_pages = [page for page in raw_pages
                     if not content_types or page.get("type") in content_types]

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
    ret = dict()
    for page in raw_pages:
        label = page.get(condition)
        if label:
            if label not in ret:
                ret[label] = 1
            else:
                ret[label] += 1
    return ret