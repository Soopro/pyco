# coding=utf-8
from __future__ import absolute_import

from werkzeug.datastructures import ImmutableDict
from werkzeug.utils import secure_filename
from slugify import slugify
from datetime import datetime
from functools import cmp_to_key
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


def route_inject(app_or_blueprint, url_patterns):
    for pattern in url_patterns:
        options = pattern[3] if len(pattern) > 3 else {}
        app_or_blueprint.add_url_rule(pattern[0],
                                      view_func=pattern[1],
                                      methods=pattern[2].split(),
                                      **options)


def _slug_not_startswith_num(slug):
    if slug[:1] and slug[:1].isdigit():
        slug = u's-{}'.format(slug)
    return slug


def process_slug(value, autofill=True):
    try:
        slug = unicode(slugify(value))
    except Exception:
        slug = u''
    if not slug and autofill:
        slug = unicode(uuid.uuid4().hex[:6])
    return _slug_not_startswith_num(slug)


def slug_uuid_suffix(slug, dig=6):
    if not slug:
        return _slug_not_startswith_num(uuid.uuid4().hex[:dig])
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


def parse_sortby(sort_by):
    key = None
    direction = None
    if isinstance(sort_by, basestring):
        if sort_by.startswith('+'):
            key = sort_by.lstrip('+')
            direction = 1
        else:
            key = sort_by.lstrip('-')
            direction = -1
    elif isinstance(sort_by, tuple):
        key = sort_by[0]
        direction = sort_by[1]
    else:
        return None
    return (key, direction)


def sortedby(source, sort_keys, reverse=False):
    if isinstance(sort_keys, (basestring, tuple)):
        sort_keys = [sort_keys]
    elif not isinstance(sort_keys, list):
        sort_keys = []

    sorts = [parse_sortby(key) for key in sort_keys]

    def compare(a, b):
        for sort in sorts:
            if sort is None:
                continue
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
        if len(str(int(date))) == 13:
            date = int(date / 1000)
        try:
            date_object = datetime.fromtimestamp(date)
        except Exception:
            return date
    else:
        return date

    try:
        if isinstance(to_format, unicode):
            to_format = to_format.encode('utf-8')
        _formatted = date_object.strftime(to_format)
        date_formatted = _formatted.decode('utf-8')
    except Exception:
        date_formatted = date
    return date_formatted


def to_timestamp(date, input_datefmt='%Y-%m-%d'):
    if isinstance(date, basestring):
        try:
            date = datetime.strptime(date, input_datefmt)
        except Exception:
            return 0
    elif not isinstance(date, datetime.datetime):
        return 0
    return int((date - datetime(1970, 1, 1)).total_seconds())


def time_age(date, gap=None, input_datefmt='%Y-%m-%d'):
    if not isinstance(gap, int):
        gap = 3600 * 24 * 365
    if isinstance(date, basestring):
        try:
            dt = datetime.strptime(date, input_datefmt)
            dt_stamp = (dt - datetime(1970, 1, 1)).total_seconds()
        except Exception:
            return None
    elif isinstance(date, int):
        if len(str(date)) == 13:
            date = int(date / 1000)
        dt_stamp = date
    elif isinstance(date, datetime.datetime):
        dt_stamp = (date - datetime(1970, 1, 1)).total_seconds()
    else:
        return None
    try:
        age = int(int(time.time()) - dt_stamp) / gap
    except Exception:
        return None
    return age


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


# price
def convert_price(amount, use_currency=False, symbol=u'', fraction_size=2):
    pattern = u'{:,.{size}f}' if use_currency else u'{:.{size}f}'
    try:
        price = pattern.format(int(amount) / 100.0, size=fraction_size)
    except Exception:
        price = None
    return u'{}{}'.format(symbol, price)
