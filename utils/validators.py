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
    if re.match(r"^[\w-]+(\.[\w-]+)*@([\w-]+\.)+[a-zA-Z]+$", val) and \
       max_length(100)(val):
        return True
    else:
        return False


def login_validator(val):
    if not val:
        return False
    return email_validator(val)


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
