# coding=utf-8
from __future__ import absolute_import

from flask import make_response
from functools import wraps
import json


def output_json(f):
    @wraps(f)
    def decorate(*args, **kwargs):
        result = f(*args, **kwargs)
        return make_json_response(result)
    return decorate


def make_json_response(output, status_code):
    headers = dict()
    headers["Content-Type"] = "application/json"
    resp = make_response(json.dumps(output), status_code, headers)
    return resp


def make_content_response(output, status_code, etag=None):
    response = make_response(output, status_code)
    response.cache_control.public = "public"
    response.cache_control.max_age = 60 * 10
    if etag is not None:
        response.set_etag(etag)
    return response


def make_cors_headers(mime_type):
    headers = dict()
    headers["Content-Type"] = mime_type
    base_set = ["origin", "accept", "content-type", "authorization"]
    headers["Access-Control-Allow-Headers"] = ", ".join(base_set)
    headers_options = "OPTIONS, HEAD, POST, PUT, DELETE"
    headers["Access-Control-Allow-Methods"] = headers_options
    headers["Access-Control-Allow-Origin"] = '*'
    headers["Access-Control-Max-Age"] = 60 * 60 * 24
    return headers
