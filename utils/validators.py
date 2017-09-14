# coding=utf-8
from __future__ import absolute_import

import re


def all_valid(*args):
    def validate(value):
        return all(f(value) for f in args)

    return validate


def non_empty(value):
    if not value:
        return False
    return True


def max_length(length):
    def validate(value):
        try:
            if len(value) > length:
                return False
            else:
                return True
        except Exception:
            return False

    return validate


def email_validator(val):
    if not val:
        return False
    if re.match(r'^[\w-]+(\.[\w-]+)*@([\w-]+\.)+[a-zA-Z]+$', val) and \
       max_length(100)(val):
        return True
    else:
        return False


def url_validator(val):
    return _url_validator(val)


def ensure_absurl(src, url_base):
    if not src:
        return ''
    if _url_validator(src):
        return src
    else:
        return '{}/{}'.format(url_base.rstrip('/'), src.lstrip('/'))


def _url_validator(val):
    if not val or not isinstance(val, basestring):
        return False
    try:
        # re.match(r'^(?:http|ftp)s?://', val)
        return bool(re.match(r'^(?:[\w]+:)?\/\/[a-zA-Z0-9]', val, flags=re.I))
    except Exception:
        return False
