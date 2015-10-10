#coding=utf-8
from __future__ import absolute_import
import os, re, gettext, json
from flask import make_response


def load_config(app, config_name="config.py"):
    app.config.from_pyfile(config_name)
    app.config.setdefault("DEBUG", False)
    app.config.setdefault("BASE_URL", "/")
    app.config.setdefault("BASE_PATH", "")
    app.config.setdefault("LIBS_URL", "http://libs.soopro.com")
    app.config.setdefault("PLUGINS", [])
    app.config.setdefault("IGNORE_FILES", [])
    app.config.setdefault("INVISIBLE_PAGE_LIST",[])
    app.config.setdefault("THEME_NAME", "default")
    app.config.setdefault("HOST", "0.0.0.0")
    app.config.setdefault("PORT", 5500)
    app.config.setdefault("EDITOR_PORT", 5550)
    app.config.setdefault("SITE",{})
    app.config.setdefault("THEME_META",{})
    app.config.setdefault("CHARSET","utf8")
    app.config.setdefault("SYS_ICON_LIST",[])
    
    app.config.setdefault("MAX_MODE_TYPES",["ws"])
    app.config.setdefault("PLUGIN_DIR","plugins")
    app.config.setdefault("THEMES_DIR","themes")
    app.config.setdefault("TEMPLATE_FILE_EXT",".html")
    app.config.setdefault("TPL_FILE_EXT",".tpl")

    app.config.setdefault("DEFAULT_SITE_META_FILE","site.json")
    app.config.setdefault("DEFAULT_THEME_META_FILE","config.json")
    
    app.config.setdefault("DEFAULT_TEMPLATE","index")
    
    app.config.setdefault("DEFAULT_DATE_FORMAT","%Y-%m-%d")
    app.config.setdefault("DEFAULT_EXCERPT_LENGTH",50)
    app.config.setdefault("DEFAULT_EXCERPT_ELLIPSIS","&hellip;")
    
    app.config.setdefault("STATIC_BASE_URL","/static")
    app.config.setdefault("UPLOADS_DIR","uploads")
    app.config.setdefault("THUMBNAILS_DIR","thumbnails")
    app.config.setdefault("CONTENT_DIR","content")
    app.config.setdefault("CONTENT_FILE_EXT",".md")
    app.config.setdefault("DEFAULT_INDEX_ALIAS","index")
    app.config.setdefault("DEFAULT_404_ALIAS","error_404")
    
    return


def make_content_response(output, status_code, etag=None):
    response = make_response(output, status_code)
    response.cache_control.public = "public"
    response.cache_control.max_age = 600
    if etag is not None:
        response.set_etag(etag)
    return response
    

def helper_process_url(url, base_url):
    if not url or not isinstance(url,(str,unicode)):
        return None

    if re.match("^(?:http|ftp)s?://", url):
        return url
    else:
        base_url = os.path.join(base_url, '')
        url = os.path.join(base_url, url.strip('/'))
        return url


from functools import cmp_to_key
def sortby(source, sort_keys, reverse = False):
    keys = {}
    
    def process_key(key):
        if key.startswith('-'):
            key = key.lstrip('-')
            revs = -1
        else:
            key = key.lstrip('+')
            revs = 1
        keys.update({key: revs})
         
    if isinstance(sort_keys, (str, unicode)):
        process_key(sort_keys)
    elif isinstance(sort_keys, list):
        for key in sort_keys:
            if not isinstance(key, (str, unicode)):
                continue
            process_key(key)

    def compare(a, b):
        for key, value in keys.iteritems():
            if a.get(key) < b.get(key):
                return -1 * value
            if a.get(key) > b.get(key):
                return 1 * value
        return 0

    return sorted(source, key = cmp_to_key(compare), reverse = reverse)
    

from werkzeug.datastructures import ImmutableDict
class DottedImmutableDict(ImmutableDict):
    def __getattr__(self, item):
        try:
            v = self.__getitem__(item)
        except KeyError:
            # ImmutableDict will take care rest errors.
            return ''
        if isinstance(v, dict):
            v = DottedImmutableDict(v)
        return v

def helper_make_dotted_dict(obj):
    if isinstance(obj, dict):
        return DottedImmutableDict(obj)
    elif isinstance(obj, list):
        new_obj = []
        for i in obj:
            new_obj.append(DottedImmutableDict(i))
        return new_obj
    else: 
        return obj
        

def url_validator(val):
    if not val:
        return False
    try:
        if re.match("^[\w]+:", val):
            return True
        else:
            return False
    except:
        return False
        
