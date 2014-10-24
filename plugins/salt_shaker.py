#coding=utf-8
from __future__ import absolute_import


def before_render(var,template):
    var["saltshaker"] = salt_shaker
    return

#custom functions
def salt_shaker(obj, conditions, intersection = False):
    results = None
    if not isinstance(conditions, list) or len(conditions)>10:
        return "Excessive"
    if isinstance(obj, list):
        results = []
    elif isinstance(obj, dict):
        results = {}
    
    first=True
    for cond in conditions:
        
        if isinstance(obj, list):
            if intersection and not first:
                results = [i for i in results if i.get(cond)]
            else:
                for i in obj:
                    if i.get(cond) and i not in results:
                        results.append(i);
                    
        elif isinstance(obj, dict):
            if intersection and not first:
                results.update({k:v for (k, v) in results.iteritems() if k == cond and v})
            else:
                results.update({k:v for (k, v) in obj.iteritems() if k == cond and v})
                
        if first:
            first = False

    return results
