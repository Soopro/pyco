#coding=utf-8
from __future__ import absolute_import

DEBUG = False
PORT = 5000

THEME_NAME = "default"

BASE_URL = "http://localhost:5000"

SITE_META = {
    "title": "Test Website Title",
    "author": "DTynn",
    "description": "site description",
    "copyright": "&copy; supmice.com",
    "license": "#license",
    "translates":{
        "en_US":{"name":u"English", "text":u"Language", "url":u"http://smalltalks.cc"},
        "zh_CN":{"name":u"简体中文", "text":u"语 言", "url":u"http://cn.smalltalks.cc"}
    },
    "locale":"zh_CN"
}
THEME_META = {
    "theme_name" : THEME_NAME
}

POST_DATE_FORMAT = "%d, %b %Y"

POST_ORDER_BY = "date"
POST_ORDER = "desc"

IGNORE_FILES = []

PLUGINS = ["autometas","shortcode","redirect","draft","languages",
"content_types","sort_by_order","jinja_helpers"]

""" For Plugins """
# #languages
# TRANSLATES = {
#     "en":{"name":u"English", "text":u"Language", "url":u"http://smalltalks.cc"},
#     "zh":{"name":u"简体中文", "text":u"语 言", "url":u"http://cn.smalltalks.cc"}
# }
# TRANSLATE_REDIRECT = False
#shortcodes
SHORTCODES  = [
    {"pattern":"base_url","replacement":""},
    {"pattern":"uploads","replacement":"/uploads"},
    {"pattern":"image_url","replacement":"/uploads"}
]

ADDITIONAL_METAS = ["nav","link","target","parent","thumbnail"]