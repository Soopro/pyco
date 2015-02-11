#coding=utf-8
from __future__ import absolute_import

DEBUG = True

HOST = '0.0.0.0'
PORT = 5500

THEME_NAME = 'default'

BASE_URL = "http://127.0.0.1:5500/"

SITE_META = {
    "title": "DevinPan",
    "author": "pan",
    "description": "A invincible super high-end photographer devin pan's website",
    "copyright": "&copy; devinPan.com",
    "license": "#license",
    "locale": "zh_CN"
}


IGNORE_FILES = []

PLUGINS = ["autometas",
           "redirect",
           "draft",
           "languages",
           "content_types",
           "jinja_helper"]

""" For Plugins """
