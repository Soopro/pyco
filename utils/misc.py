# coding=utf-8
from __future__ import absolute_import

from werkzeug.datastructures import ImmutableDict
from werkzeug.utils import secure_filename
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


class SilentlyStr(str):
    def return_new(*args, **kwargs):
        return SilentlyStr('')

    def silently(*args, **kwargs):
        return ''

    __getattr__ = return_new
    __call__ = return_new
    __unicode__ = silently
    __str__ = silently


class DottedImmutableDict(ImmutableDict):
    def __getattr__(self, item):
        try:
            v = self.__getitem__(item)
        except KeyError:
            # do not use None, it could be use by a loop.
            # None is not iterable.
            return SilentlyStr()
        if isinstance(v, dict):
            v = DottedImmutableDict(v)
        return v


def make_dotted_dict(obj):
    if isinstance(obj, dict):
        return DottedImmutableDict(obj)
    elif isinstance(obj, list):
        return [make_dotted_dict(o) for o in obj]
    else:
        return obj


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


def process_slug(value, ensure=True):
    try:
        slug = unicode(slugify(value))
    except Exception:
        slug = u''
    if not slug and ensure:
        slug = unicode(repr(time.time())).replace('.', '-')
    return slug


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


def remove_multi_space(text):
    if isinstance(text, str):
        text = text.decode('utf-8')
    elif not isinstance(text, unicode):
        return u''
    return re.sub(r'\s+', ' ', text).replace('\n', ' ').replace('\b', ' ')


def make_sorts_rule(sort_by, initial=None):
    if initial and isinstance(initial, list):
        sort_rules = [item for item in initial
                      if isinstance(item, (basestring, tuple))]
    else:
        sort_rules = []

    if isinstance(sort_by, (basestring, tuple)):
        sort_rules.append(sort_by)
    elif isinstance(sort_by, list):
        sort_rules = sort_rules + [key for key in sort_by
                                   if isinstance(key, (basestring, tuple))]
    return sort_rules


def sortedby(source, sort_keys, reverse=False):
    sorts = []
    if not isinstance(sort_keys, list):
        sort_keys = [sort_keys]

    def parse_sorts(key):
        if isinstance(key, tuple):
            sorts.append((key[0], key[1]))
        elif isinstance(key, basestring):
            if key.startswith('-'):
                key = key.lstrip('-')
                direction = -1
            else:
                key = key.lstrip('+')
                direction = 1
            sorts.append((key, direction))

    for key in sort_keys:
        parse_sorts(key)

    def compare(a, b):
        for sort in sorts:
            key = sort[0]
            direction = sort[1]
            if a.get(key) < b.get(key):
                return -1 * direction
            if a.get(key) > b.get(key):
                return 1 * direction
        return 0

    return sorted(source, key=cmp_to_key(compare), reverse=reverse)


def parse_int(num, default=0, natural=False):
    if not isinstance(default, int):
        default = 0
    if not isinstance(natural, (int, bool)):
        natural = False
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
        str_ver_list = str_version.split('.')[:4]
        version = [int(v) for v in str_ver_list[:3]]
        if len(str_ver_list) > 3:
            version.append(str_ver_list[3])
    except:
        version = None
    return version


def version_list_to_str(list_version):
    try:
        list_version += [0, 0, 0]  # ensure has 3 items
        version = '.'.join(map(str, list_version[:4]))
    except:
        version = None
    return version


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


def match_cond(target, cond_key, cond_value, force=True, opposite=False):
    """
    params:
    - target: the source data want to check.
    - cond_key: the attr key of condition.
    - cond_value: the value of condition.
      if the cond_value is a list, any item matched will make output matched.
    - opposite: reverse check result.
    - force: must have the value or not.
    """

    def _dotted_get(key, obj):
        if not isinstance(obj, dict):
            return None
        elif '.' not in key:
            return obj.get(key)
        else:
            key_pairs = key.split('.', 1)
            obj = obj.get(key_pairs[0])
            return _dotted_get(key_pairs[1], obj)

    def _dotted_in(key, obj):
        if not isinstance(obj, dict):
            return False
        elif '.' not in key:
            return key in obj
        else:
            key_pairs = key.split('.', 1)
            obj = obj.get(key_pairs[0])
            return _dotted_in(key_pairs[1], obj)

    if cond_value == '' and not force:
        return _dotted_in(cond_key, target) != opposite
    elif cond_value is None and not force:
        # if cond_value is None will reverse the opposite,
        # then for the macthed opposite must reverse again. so...
        # also supported if the target value really is None.
        return _dotted_in(cond_key, target) == opposite
    elif isinstance(cond_value, bool) and not force:
        return _dotted_in(cond_key, target) != opposite
    elif not _dotted_in(cond_key, target):
        return False

    matched = False
    target_value = _dotted_get(cond_key, target)
    if isinstance(cond_value, list):
        for c_val in cond_value:
            matched = match_cond(target, cond_key, c_val, force=True)
            if matched:
                break
    elif isinstance(cond_value, bool):
        target_bool = isinstance(target_value, bool)
        matched = cond_value == target_value and target_bool
    else:
        if isinstance(target_value, list):
            matched = cond_value in target_value
        else:
            matched = cond_value == target_value

    return matched != opposite
