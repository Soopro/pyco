# coding=utf-8
from __future__ import absolute_import

from flask import request


def _empty_value(value):
    return value is not False and value != 0 and not bool(value)


def get_param(key, validator=None, required=False, default=None):
    source = request.json
    value = source.get(key)

    if _empty_value(value):
        if default is not None:
            value = default
        elif required:
            raise Exception('Param key error.')

    if validator:
        validators = validator if isinstance(validator, list) else [validator]

        for vld in validators:
            if not hasattr(vld, '__call__'):
                continue
            vld(value, name=key, non_empty=required)

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


def make_query(args):
    query = ""
    for arg in args:
        s = "{}={}".format(arg, args.get(arg)) if query == "" \
            else "&{}={}".format(arg, args.get(arg))

        query = "{}{}".format(query, s)
    return query


def get_remote_addr():
    ip = request.headers.get('X-Forwarded-For')
    if ip:
        ip = ip.split(',', 1)[0]
    else:
        ip = request.headers.get('X-Real-IP')
    return ip or request.remote_addr
