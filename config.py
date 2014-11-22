#coding=utf-8
from __future__ import absolute_import

DEBUG = True
PORT = 5500

THEME_NAME = 'devinpan'

BASE_URL = "http://devinpan.com/"

SITE_META = {"title": "DevinPan",
             "author": "pan",
             "description": "A invincible super high-end photographer devin pan's website",
             "copyright": "&copy; devinPan.com",
             "license": "#license",
             "locale": "zh_CN"
}

THEME_META = {"content_types": {"page": "Pages",
                                },
              "theme_name": THEME_NAME,
              }

PAGE_DATE_FORMAT = "%d, %b %Y"

PAGE_ORDER_BY = "date"
PAGE_ORDER = "desc"

IGNORE_FILES = []

PLUGINS = ["autometas",
           "redirect",
           "draft",
           "languages",
           "content_types",
           "sort_by_priority",
           "jinja_helpers"]

""" For Plugins """
