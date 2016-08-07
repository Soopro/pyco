# coding=utf-8
from __future__ import absolute_import

from functools import partial
from werkzeug.datastructures import ImmutableDict
from werkzeug.utils import secure_filename
from bson import ObjectId
from slugify import slugify
from datetime import datetime
from functools import cmp_to_key
import os
import re
import time
import hashlib
import hmac
import urllib
import urlparse
import mimetypes
from flask import make_response, request
import json


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


class DottedImmutableDict(ImmutableDict):
    def __getattr__(self, item):
        try:
            v = self.__getitem__(item)
        except KeyError:
            return None
        if isinstance(v, dict):
            v = DottedImmutableDict(v)
        return v


class NamedPartial(partial):
    @property
    def __name__(self):
        return self.func.__name__


def route_inject(app_or_blueprint, url_patterns):
    for pattern in url_patterns:
        options = pattern[3] if len(pattern) > 3 else {}
        app_or_blueprint.add_url_rule(pattern[0],
                                      view_func=pattern[1],
                                      methods=pattern[2].split(),
                                      **options)


_valid_slug = re.compile(r'^[a-z0-9_\-]+$')
_word = re.compile(r'\w')
_white_space = re.compile(r'\s')


def process_slug(value):
    try:
        slug = unicode(slugify(value))
    except Exception:
        slug = None
    default_slug = unicode(repr(time.time())).replace('.', '-')
    return slug or default_slug


def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except ValueError:
        return default


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


def sleep(t):
    time.sleep(t)


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


def safe_regex_str(val):
    if isinstance(val, unicode):
        val = val.decode("utf-8")
    elif not isinstance(val, str):
        return None
    val = val.replace("/", "\/")
    val = val.replace("*", "\*")
    val = val.replace(".", "\.")
    val = val.replace("[", "\[")
    val = val.replace("]", "\]")
    val = val.replace("(", "\(")
    val = val.replace(")", "\)")
    val = val.replace("^", "\^")
    val = val.replace("|", "\|")
    val = val.replace("{", "\{")
    val = val.replace("}", "\}")
    val = val.replace("?", "\?")
    val = val.replace("$", "\$")
    return val


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


def parse_dict_by_structure(obj, structure):
    if not isinstance(obj, dict):
        return None
    newobj = {}
    for k, v in structure.iteritems():
        if type(obj.get(k)) is not v:
            newobj.update({k: v()})
        else:
            newobj.update({k: obj.get(k)})
    return newobj


def version_str_to_list(str_version):
    try:
        version = [int(v) for v in str_version.split('.')]
        assert len(version) == 3
    except:
        version = None
    return version


def version_list_to_str(list_version):
    try:
        list_version += [0, 0, 0]  # ensure has 3 items
        list_version = list_version[0:3]
        version = '.'.join(map(str, list_version))
    except:
        version = None
    return version


def is_ObjectId(_id):
    return _id and ObjectId.is_valid(_id)


def safe_filename(filename, mimetype=None):
    _starts = re.match(r'_*', filename)
    # this is for filename starts with one or many '_'

    if not mimetype:
        try:
            mimetype = mimetypes.guess_type(filename)[0]
        except:
            mimetype = None

    filename = secure_filename(filename)
    name, ext = os.path.splitext(filename)
    if not name:
        time_now = int(time.time())
        name = u'unknow_filename_{}'.format(time_now)
    if not ext and mimetype:
        ext = mimetypes.guess_extension(mimetype)
        ext = ext if ext else '.{}'.format(mimetypes.split('/')[-1])
    filename = u"{}{}".format(name, ext)
    return u"{}{}".format(_starts.group(), filename)


def file_md5(fname):
    _hash = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            _hash.update(chunk)
    return _hash.hexdigest()


def hmac_sha(key, msg, digestmod=None, output=True):
    if digestmod is None:
        digestmod = hashlib.sha1
    sha = hmac.new(str(key), str(msg), digestmod=digestmod)
    if output:
        return sha.hexdigest()
    else:
        return sha


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


def str2unicode(text):
    if isinstance(text, str):
        return text.decode('utf-8')
    return text


def unicode2str(text):
    if isinstance(text, unicode):
        return text.encode('utf-8')
    return text
