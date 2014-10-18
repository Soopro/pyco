#coding=utf-8
from __future__ import absolute_import

_CONFIG = {}
_ORDER_DESC = False
_ORDER_BY = 'date'

def config_loaded(config):
    global _ORDER_DESC
    global _ORDER_BY
    
    _CONFIG.update(config)
    if _CONFIG.get('POST_ORDER') == 'desc':
        _ORDER_DESC = True

    _ORDER_BY = _CONFIG.get('POST__ORDER_BY') or _ORDER_BY
    return


def request_url(request):
    global URL
    URL = request.path
    return

def get_post_data(data, post_meta):
    data["order"] = post_meta.get("order") or None
    return

def get_posts(posts, current_post, prev_post, next_post):
    ordered_pages = []
    for post in posts:
        try: 
            order = int(post.get('order'))
        except Exception:
            order = None

        post['order'] =  order or 0
        ordered_pages.append(post);
    
    posts = sort_order(ordered_pages,'order', _ORDER_BY)
    return
    
def sort_order(posts, param, param_order_by):
    if len(posts) < 1:
        return posts
    
    pivot = posts[0]
    left_list = []
    right_list = []
    
    for post in posts:
        if post['order']>pivot['order']:
            left_list.append(post)
        else:
            right_list.append(post)

    left_list = sort_order(left_list, param, param_order_by)
    right_list = sort_order(right_list, param, param_order_by)
    
    return left_list + [pivot] + right_list
        
def compare(a,b,param,param_order_by):
    
    if a[param] != b[param]:
        if _ORDER_DESC:
            return a[param] > b[param]
        else:
            return a[param] < b[param]
    else:
        if a.get(param_order_by) and b.get(param_order_by):
            if _ORDER_DESC:
                return a[param_order_by] > b[param_order_by]
            else:
                return a[param_order_by] < b[param_order_by]
        else:
            return True