# coding=utf-8
from __future__ import absolute_import
from flask import make_response, request
from werkzeug.datastructures import ImmutableDict
import re
import json
import urllib
import urlparse
import time
from datetime import datetime
from functools import cmp_to_key


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

    app.config.setdefault("STATIC_PATH", "static")
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
        return "{}/{}".format(base_url, url.strip('/'))


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


def parse_int(num, default=0, natural=False):
    try:
        num = int(float(num))
    except:
        num = default
    if natural == 0:
        num = max(0, num)
    elif natural:
        num = max(1, num)
    return num


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


def now(dig=10):
    if dig == 10:
        return int(time.time())
    elif dig == 11:
        return int(time.time() * 10)
    elif dig == 12:
        return int(time.time() * 100)
    elif dig == 13:
        return int(time.time() * 1000)
    elif dig == 14:
        return int(time.time() * 10000)
    elif dig == 15:
        return int(time.time() * 100000)
    elif dig == 16:
        return int(time.time() * 1000000)
    else:
        return time.time()


def get_url_params(url, unique=True):
    url_parts = list(urlparse.urlparse(url))
    url_params = urlparse.parse_qsl(url_parts[4])
    if unique:
        params = dict(url_params)
    else:
        params = {}
        for param in url_params:
            k = param[0]
            v = param[1]
            if k in params:
                if not isinstance(params[k], list):
                    params[k] = [params[k]]
                params[k].append(v)
            else:
                params[k] = v
    return params


def add_url_params(url, new_params, concat=True, unique=True):
    def _dict2params(param_dict):
        out_params = []
        for k, v in param_dict.iteritems():
            if isinstance(v, list):
                for i in v:
                    out_params.append((k, i))
            else:
                out_params.append((k, v))
        return out_params

    if isinstance(new_params, dict):
        new_params = _dict2params(new_params)
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


def format_date(date, to_format, input_datefmt="%Y-%m-%d"):
    if not to_format:
        return date
    if isinstance(date, basestring):
        try:
            date_object = datetime.strptime(date, input_datefmt)
        except Exception:
            return date

    elif isinstance(date, int):
        if len(str(date)) == 13:
            date = int(date / 1000)
        try:
            date_object = datetime.fromtimestamp(date)
        except Exception:
            return date
    else:
        return date

    try:
        _formatted = date_object.strftime(to_format.encode('utf-8'))
        date_formatted = _formatted.decode('utf-8')
    except Exception:
        date_formatted = date
    return date_formatted
