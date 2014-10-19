#coding=utf-8
from __future__ import absolute_import

_CONFIG = {}
_DEFAULT_CONTENT_TYPE = 'page'
_URL = ''

def config_loaded(config):
    global _CONFIG
    _CONFIG = config
    return

            
def request_url(request, redirect_to):
    global _URL
    _URL = request.path
    return

def get_post_data(data, post_meta):
    data["type"] = post_meta.get("type") or None
    filter_auto_type(data,data.get("url"));
    return

def single_post_meta(post_meta, redirect_to):
    post_url = _CONFIG.get("BASE_URL")+_URL
    filter_auto_type(post_meta, post_url);
    return

#custom functions
def filter_auto_type(meta,post_url):
    base_url = _CONFIG.get("BASE_URL")

    if not meta.get("type"):
        relative_path = post_url.replace(base_url+"/","")
        try:
            content_type = relative_path[0:relative_path.index("/")]
        except ValueError:
            content_type = _DEFAULT_CONTENT_TYPE
    
        meta["type"] = content_type
    meta["type"] = meta["type"].lower()
    