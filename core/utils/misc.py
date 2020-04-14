# coding=utf-8

from werkzeug.utils import secure_filename
from slugify import slugify
from datetime import datetime
from functools import cmp_to_key
import os
import re
import ast
import uuid
import time
import random
import json
import hashlib
import hmac
import urllib
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
        slug = 's-{}'.format(slug)
    return slug


def process_slug(value, autofill=True):
    try:
        slug = str(slugify(value))
    except Exception:
        slug = ''
    if not slug and autofill:
        slug = str(uuid.uuid4().hex[:6])
    return _slug_not_startswith_num(slug)


def slug_uuid_suffix(slug, dig=6):
    if not slug:
        return _slug_not_startswith_num(uuid.uuid4().hex[:dig])
    return '{}-{}'.format(slug, uuid.uuid4().hex[:dig])


def uuid4_hex(dig=32):
    return str(uuid.uuid4().hex[:dig])


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


def add_url_params(url, input_params, unique=True, concat=True):
    if isinstance(input_params, dict):
        # make sure all value as list
        input_params = {k: v if isinstance(v, list) else [v]
                        for k, v in input_params.items()}
    elif isinstance(input_params, str):
        input_params = {input_params: ['']}
    else:
        return ''

    result = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(result.query, keep_blank_values=True)

    if concat:
        for k, v in input_params.items():
            if k in params:
                if isinstance(params[k], list):
                    params[k] += v
                else:
                    params[k] = [params[k]] + v
            else:
                params[k] = v
    else:
        params = input_params

    if unique:
        params = {k: v[-1] if unique else v for k, v in params.items()}

    for k, v in params.items():
        if isinstance(v, str):
            v = v.encode('utf-8')
        elif isinstance(v, list):
            v = [i.encode('utf-8') if isinstance(i, str) else i
                 for i in v]
        params[k] = v

    result = list(result)
    try:
        params_str = urllib.parse.urlencode(params, True)
        result[4] = params_str.replace('=&', '&').strip('=')
    except Exception as e:
        result[4] = str(e)

    return urllib.parse.urlunparse(result)


def get_url_params(url, unique=True):
    result = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(result.query, keep_blank_values=True)
    if unique:
        params = {k: v[-1] for k, v in params.items()}
    return params


def gen_excerpt(raw_text, excerpt_length, ellipsis_mark='&hellip;'):
    excerpt = re.sub(r'[\r\b\n]', '', raw_text, flags=re.MULTILINE).strip()
    excerpt = re.sub(r'<.*?>', '', excerpt, flags=re.MULTILINE).strip()
    excerpt_ellipsis = ellipsis_mark if len(excerpt) > excerpt_length else ''
    return '{}{}'.format(excerpt[:excerpt_length], excerpt_ellipsis)


def safe_regex_str(val):
    if not isinstance(val, str):
        return ''
    return re.sub(r'[\/\\*\.\[\]\(\)\^\|\{\}\?\$\!\@\#]', '', val)


def remove_multi_space(text):
    if not isinstance(text, str):
        return ''
    return re.sub(r'\s+', ' ', text).replace('\n', ' ').replace('\b', ' ')


def parse_sortby(sort_by):
    key = None
    direction = None
    if isinstance(sort_by, str):
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
    if isinstance(sort_keys, (str, tuple)):
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


def parse_int(num, default=0, minimum=None):
    if not isinstance(default, int):
        default = 0
    if isinstance(minimum, float):
        minimum = int(minimum)
    try:
        num = int(float(num))
    except (ValueError, TypeError):
        num = default
    if isinstance(minimum, int):
        num = max(minimum, num)
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
        name = 'unknow_filename_{}'.format(time_now)
    if not ext and mimetype:
        ext = mimetypes.guess_extension(mimetype)
        ext = ext if ext else '.{}'.format(mimetypes.split('/')[-1])
    filename = '{}{}'.format(name, ext)
    return '{}{}'.format(_starts.group(), filename)


def hmac_sha(key, msg, digestmod=None, use_hexdigest=True):
    if digestmod is None:
        digestmod = hashlib.sha256
    sha = hmac.new(bytes(key, 'utf-8'),
                   bytes(msg, 'utf-8'),
                   digestmod=digestmod)
    if use_hexdigest:
        return sha.hexdigest()
    else:
        return sha


def parse_dateformat(date, to_format, input_datefmt='%Y-%m-%d'):
    if not to_format:
        return date
    if isinstance(date, str):
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
        date_formatted = date_object.strftime(to_format)
    except Exception:
        date_formatted = date
    return date_formatted


def to_timestamp(date, input_datefmt='%Y-%m-%d'):
    if isinstance(date, str):
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
    if isinstance(date, str):
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


def match_cond(target, cond_key, cond_value, opposite=False):
    """
    params:
    - target: the source data want to check.
    - cond_key: the attr key of condition.
    - cond_value: the value of condition.
      if the cond_value is a list, any item matched will make output matched.
    - opposite: reverse check result.
    """

    def _dotted_get(key, obj):
        if '.' not in key:
            try:
                return obj.get(key)
            except Exception:
                return None
        else:
            key_pairs = key.split('.', 1)
            try:
                _obj = obj.get(key_pairs[0])
            except Exception:
                return None
            return _dotted_get(key_pairs[1], _obj)

    matched = False
    target_value = _dotted_get(cond_key, target)

    if isinstance(cond_value, list):
        for c_val in cond_value:
            matched = match_cond(target, cond_key, c_val, force=True)
            if matched:
                break
    else:
        if isinstance(target_value, list):
            matched = cond_value in target_value
        else:
            matched = cond_value == target_value

    if opposite:
        return not matched
    else:
        return matched


# mimetypes
def split_file_ext(filename):
    try:
        return os.path.splitext(filename)[1][1:].lower()
    except Exception:
        return None


def split_file_type(filename, fail_mimetype=None):
    mimetype = guess_mimetype(filename, fail_mimetype)

    if isinstance(mimetype, str):
        return mimetype.split('/')[0]
    else:
        return mimetype


def guess_mimetype(filename, default=None):
    try:
        guessed_type = mimetypes.guess_type(filename)[0]
    except Exception:
        guessed_type = None
    mimetype = guessed_type or default
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


# replace
def replace_startswith(text, target_str, replacement, count=1):
    if isinstance(text, str) and text.startswith(target_str):
        text = text.replace(target_str, replacement, count)
        # use `count` = 1 to replace every matched.
    return text


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

    for i in range(limit):
        rand = _random_item(seq)
        if rand is not None:
            selected.append(rand)
        else:
            break
    return selected


# price
def convert_price(amount, use_currency=False, symbol='', fraction_size=2):
    pattern = '{:,.{size}f}' if use_currency else '{:.{size}f}'
    try:
        price = pattern.format(int(amount) / 100.0, size=fraction_size)
    except Exception:
        price = None
    return '{}{}'.format(symbol, price)


# chunks
def chunks(raw_list, group_size=12):
    for i in range(0, len(raw_list), max(group_size, 1)):
        yield raw_list[i:i + group_size]


# eval
def str_eval(s, default=None):
    try:
        return ast.literal_eval(s)
    except Exception as e:
        if default is not None:
            return default
        else:
            raise e


# data
def parse_json(s, default=None):
    try:
        return json.loads(s)
    except Exception as e:
        if default is not None:
            return default
        else:
            raise e


def get_from_dict(obj, key, format_class=None, default=None):
    try:
        result = obj.get(key, default)
    except Exception:
        result = default

    if callable(format_class) and not isinstance(result, format_class):
        result = format_class()
    return result
