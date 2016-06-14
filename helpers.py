# coding=utf-8
from __future__ import absolute_import
import os
import re
import gettext
import json
import urllib
import urlparse
import time
from flask import make_response, request


def load_config(app, config_name="config.py"):
    app.config.from_pyfile(config_name)
    app.config.setdefault("DEBUG", False)
    app.config.setdefault("BASE_URL", "/")
    app.config.setdefault("BASE_PATH", "")
    app.config.setdefault("LIBS_URL", "http://libs.soopro.com")
    app.config.setdefault("PLUGINS", [])
    app.config.setdefault("IGNORE_FILES", [])
    app.config.setdefault("INVISIBLE_PAGE_LIST", [])
    app.config.setdefault("THEME_NAME", "default")
    app.config.setdefault("HOST", "0.0.0.0")
    app.config.setdefault("PORT", 5500)
    app.config.setdefault("SITE", {})
    app.config.setdefault("THEME_META", {})
    app.config.setdefault("CHARSET", "utf8")
    app.config.setdefault("SYS_ICON_LIST", [])

    app.config.setdefault("MAX_MODE_TYPES", ["ws"])
    app.config.setdefault("PLUGIN_DIR", "plugins")
    app.config.setdefault("THEMES_DIR", "themes")
    app.config.setdefault("TEMPLATE_FILE_EXT", ".html")
    app.config.setdefault("TPL_FILE_EXT", ".tpl")

    app.config.setdefault("DEFAULT_SITE_META_FILE", "site.json")
    app.config.setdefault("DEFAULT_THEME_META_FILE", "config.json")

    app.config.setdefault("DEFAULT_TEMPLATE", "index")

    app.config.setdefault("DEFAULT_DATE_FORMAT", "%Y-%m-%d")
    app.config.setdefault("DEFAULT_EXCERPT_LENGTH", 162)
    app.config.setdefault("DEFAULT_EXCERPT_ELLIPSIS", "&hellip;")

    app.config.setdefault("STATIC_BASE_URL", "/static")
    app.config.setdefault("UPLOADS_DIR", "uploads")
    app.config.setdefault("CONTENT_DIR", "content")
    app.config.setdefault("CONTENT_FILE_EXT", ".md")
    app.config.setdefault("DEFAULT_INDEX_SLUG", "index")
    app.config.setdefault("DEFAULT_404_SLUG", "error_404")

    return


def make_json_response(output, status_code):
    headers = dict()
    headers["Content-Type"] = "application/json"
    resp = make_response(json.dumps(output), status_code, headers)
    return resp


def make_content_response(output, status_code, etag=None):
    response = make_response(output, status_code)
    response.cache_control.public = "public"
    response.cache_control.max_age = 600
    if etag is not None:
        response.set_etag(etag)
    return response


def _empty_value(value):
    return value is not False and value != 0 and not bool(value)

def get_param(key, required=False, default=None):
    source = request.json
    value = source.get(key)

    if _empty_value(value):
        if default is not None:
            value = default
        elif required:
            raise Exception('Param key error.')

    return value


def get_args(key, required=False, default=None, multiple=False):
    source = request.args
    if multiple:
        value = source.getlist(key)
    else:
        value = source.get(key)

    if _empty_value(value):
        if default is not None:
            value = default
        elif required:
            raise Exception('Args key error.')

    return value


def parse_args():
    new = dict()
    args = request.args
    for arg in args:
        if arg in new:
            if not isinstance(new[arg], list):
                new[arg] = [new[arg]]
            new[arg].append(args.get(arg))
        else:
            new[arg] = args.get(arg)
    return new


def helper_process_url(url, base_url):
    if not url or not isinstance(url, (str, unicode)):
        return None

    if re.match("^(?:http|ftp)s?://", url):
        return url
    else:
        base_url = os.path.join(base_url, '')
        url = os.path.join(base_url, url.strip('/'))
        return url


from functools import cmp_to_key


def sortedby(source, sort_keys, reverse=False):
    keys = {}

    def process_key(key):
        if key.startswith('-'):
            key = key.lstrip('-')
            revs = -1
        else:
            key = key.lstrip('+')
            revs = 1
        keys.update({key: revs})

    if isinstance(sort_keys, basestring):
        process_key(sort_keys)
    elif isinstance(sort_keys, list):
        for key in sort_keys:
            if not isinstance(key, basestring):
                continue
            process_key(key)

    def compare(a, b):
        for key, value in keys.iteritems():
            if a.get(key) < b.get(key):
                return -1 * value
            if a.get(key) > b.get(key):
                return 1 * value
        return 0

    return sorted(source, key=cmp_to_key(compare), reverse=reverse)


def parse_int(num):
    try:
        return int(float(num))
    except:
        return 0


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
            new_obj.append(helper_make_dotted_dict(i))
        return new_obj
    else:
        return obj


def url_validator(val):
    if not isinstance(val, basestring):
        return False
    try:
        # if re.match("^(?:http|ftp)s?://", val):
        if re.match(r"^\w+:", val):
            return True
        else:
            return False
    except:
        return False


def now(int_output=True):
    if int_output:
        return int(time.time())
    else:
        return time.time()


def get_url_params(url, unique=True):
    url_parts = list(urlparse.urlparse(url))
    params = urlparse.parse_qsl(url_parts[4])
    if unique:
        params = dict(params)
    return params


def add_url_params(url, new_params, concat=True, unique=True):
    if isinstance(new_params, dict):
        new_params = [(k, v) for k, v in new_params.iteritems()]
    elif isinstance(new_params, basestring):
        new_params = [(new_params, new_params)]
    elif not isinstance(new_params, list):
        return None

    url_parts = list(urlparse.urlparse(url))
    params = urlparse.parse_qsl(url_parts[4])

    params = new_params if not concat else params + new_params

    if unique:
        params = dict(params)

    url_parts[4] = urllib.urlencode(params)

    return urlparse.urlunparse(url_parts)
