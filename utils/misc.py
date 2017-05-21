# coding=utf-8
from __future__ import absolute_import

from werkzeug.datastructures import ImmutableDict
from werkzeug.utils import secure_filename
from slugify import slugify
from datetime import datetime
from functools import cmp_to_key
from bson import ObjectId
import os
import re
import uuid
import time
import random
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


def process_slug(value, autofill=True):
    try:
        slug = unicode(slugify(value))
    except Exception:
        slug = u''
    if not slug and autofill:
        slug = unicode(repr(time.time())).replace('.', '-')
    return slug


def slug_uuid_suffix(slug, dig=6):
    if not slug:
        return uuid.uuid4().hex[:dig]
    return u'{}-{}'.format(slug, uuid.uuid4().hex[:dig])


def uuid4_hex(dig=32):
    return unicode(uuid.uuid4().hex[:dig])


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
    if isinstance(val, str):
        val = val.decode('utf-8')
    elif not isinstance(val, unicode):
        return u''
    return re.sub(r'[\/\\*\.\[\]\(\)\^\|\{\}\?\$\!\@\#]', '', val)


def remove_multi_space(text):
    if isinstance(text, str):
        text = text.decode('utf-8')
    elif not isinstance(text, unicode):
        return u''
    return re.sub(r'\s+', ' ', text).replace('\n', ' ').replace('\b', ' ')


def make_sorts_rule(sort_by, initial=None):
    sort_rules = initial if isinstance(initial, list) else []

    if isinstance(sort_by, (basestring, tuple)):
        sort_rules.append(sort_by)
    elif isinstance(sort_by, list):
        sort_rules += sort_by

    sorts_list = []
    for sort in sort_rules:
        key = None
        direction = None
        if isinstance(sort, basestring):
            if sort.startswith('+'):
                key = sort.lstrip('+')
                direction = 1
            else:
                key = sort.lstrip('-')
                direction = -1
        elif isinstance(sort, tuple):
            key = sort[0]
            direction = sort[1]
        if key:
            sorts_list.append((key, direction))

    return sorts_list


def sortedby(source, sort_keys, reverse=False):
    sorts = []
    if isinstance(sort_keys, (basestring, tuple)):
        sort_keys = [sort_keys]
    elif not isinstance(sort_keys, list):
        sort_keys = []

    for key in sort_keys:
        if isinstance(key, tuple):
            sorts.append((key[0], key[1]))
        elif isinstance(key, basestring):
            if key.startswith('+'):
                key = key.lstrip('+')
                direction = 1
            else:
                key = key.lstrip('-')
                direction = -1
            sorts.append((key, direction))

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
    except (ValueError, TypeError):
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
        if v is ObjectId:
            if ObjectId.is_valid(obj.get(k)):
                newobj.update({k: ObjectId(obj.get(k))})
            else:
                newobj.update({k: None})
        else:
            if type(obj.get(k)) is v:
                newobj.update({k: obj.get(k)})
            else:
                try:
                    _v = v(obj.get(k))
                except Exception:
                    _v = v()
                newobj.update({k: _v})
    return newobj


def limit_dict(dict_obj, length=None):
    if not isinstance(dict_obj, dict):
        return {}
    elif not length or len(dict_obj) <= length:
        return dict(dict_obj)
    else:
        obj = {}
        for k, v in dict_obj.iteritems():
            if len(obj) < length:
                obj[k] = v
            else:
                break
        return obj


def version_str_to_list(str_version):
    try:
        str_ver_list = str_version.split('.')[:4]
        version = [int(v) for v in str_ver_list[:3]]
        if len(str_ver_list) > 3:
            version.append(str_ver_list[3])
    except Exception:
        version = None
    return version


def version_list_to_str(list_version):
    try:
        # ensure has 3 items
        if len(list_version) < 3:
            for x in range(3 - len(list_version)):
                list_version.append(0)
        version = '.'.join(map(unicode, list_version[:4]))
    except Exception:
        version = None
    return version


def safe_filename(filename, mimetype=None):
    _starts = re.match(r'_*', filename)
    # this is for filename starts with one or many '_'

    if not mimetype:
        try:
            mimetype = mimetypes.guess_type(filename)[0]
        except Exception:
            mimetype = None

    filename = secure_filename(filename)
    name, ext = os.path.splitext(filename)
    if not name:
        time_now = int(time.time())
        name = u'unknow_filename_{}'.format(time_now)
    if not ext and mimetype:
        ext = mimetypes.guess_extension(mimetype)
        ext = ext if ext else '.{}'.format(mimetypes.split('/')[-1])
    filename = u'{}{}'.format(name, ext)
    return u'{}{}'.format(_starts.group(), filename)


def file_md5(fname):
    _hash = hashlib.md5()
    with open(fname, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
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


def format_date(date, to_format, input_datefmt='%Y-%m-%d'):
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


def format_tags(tags, limit=60, upper=False):
    def _styl(text):
        if upper:
            return text.upper()
        else:
            return text.lower()
    tag_list = []
    tag_set = set()
    for tag in tags[:limit]:
        if not isinstance(tag, basestring):
            continue
        _tag = _styl(tag)
        if _tag not in tag_set:
            tag_set.add(_tag)
            tag_list.append(_tag)
    return tag_list


# mimetypes
def split_file_ext(filename):
    try:
        return os.path.splitext(filename)[1][1:].lower()
    except Exception:
        return None


def guess_file_type(filename, default=None, output_mimetype=True):
    try:
        guessed_type = mimetypes.guess_type(filename)[0]
    except Exception:
        guessed_type = None

    mimetype = guessed_type or default

    if not output_mimetype and mimetype:
        return mimetype.split('/')[0]
    else:
        return mimetype


# nonascii
def contains_nonascii_characters(string):
    """ check if the body contain nonascii characters"""
    for c in string:
        if not ord(c) < 128:
            return True
    return False


# escapes
def escape_asterisk(key, asterisk='*', output=None):
    if key == asterisk:
        return output
    else:
        return key


# random
def random_choices(seq, limit=1):
    seq = list(seq)
    selected = []

    def _random_item(seq):
        if not seq:
            return None
        rand = random.choice(seq)
        seq.remove(rand)
        return rand

    for i in xrange(limit):
        rand = _random_item(seq)
        if rand is not None:
            selected.append(rand)
        else:
            break
    return selected
