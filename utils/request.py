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
            try:
                value = vld(value)
            except Exception as e:
                raise Exception('ValidationError: {}\n{}'.format(key, str(e)))

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


def get_remote_addr():
    ip = request.headers.get('X-Forwarded-For')
    if ip:
        ip = ip.split(',', 1)[0]
    else:
        ip = request.headers.get('X-Real-IP')
    return ip or request.remote_addr


def get_request_url(base_url, path):
    if '?' in request.url:
        args = request.url.split('?', 1)[1]
        return '{}{}?{}'.format(base_url, path, args)
    else:
        return '{}{}'.format(base_url, path)
