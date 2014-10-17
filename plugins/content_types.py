#coding=utf-8
from __future__ import absolute_import

CONFIG = {}
DEFAULT_CONTENT_TYPE = 'page'
URL = ''

def config_loaded(config):
    CONFIG.update(config)
    return

            
def request_url(url):
    global URL
    URL = url
    return

def get_post_data(data, post_meta):
    if post_meta.get("type"):
        data["type"] = post_meta.get("type")
    
    generate_auto_type(data,data.get("url"));

    data["type"] = data["type"].lower()

    return

def single_post_meta(post_meta):
    post_url = CONFIG.get("BASE_URL")+URL
    generate_auto_type(post_meta, post_url);
    post_meta["type"] = post_meta["type"].lower()

    return
    
def generate_auto_type(meta,post_url):
    base_url = CONFIG.get("BASE_URL")

    if not meta.get("type"):
        relative_path = post_url.replace(base_url+"/","")
        try:
            content_type = relative_path[0:relative_path.index("/")]
        except ValueError:
            content_type = DEFAULT_CONTENT_TYPE
        
        meta["type"] = content_type
    