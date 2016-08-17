# coding=utf-8
from __future__ import absolute_import

from flask import make_response
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
