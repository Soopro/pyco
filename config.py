#coding=utf-8
from __future__ import absolute_import

DEBUG = True
PORT = 5000
AUTO_INDEX = True

SITE_TITLE = "TEST"
BASE_URL = "http://localhost:5000"
SITE_AUTHOR = "DTynn"
SITE_DESCRIPTION = "123123"

POST_DATE_FORMAT = "%d, %b %Y"

POST_ORDER_BY = "date"
POST_ORDER = "desc"

IGNORE_FILES = []

THEME_NAME = "tinforce"
PLUGINS = ["additional_metas","shortcode","redirect","argments","draft",
"content_types","sort_by_order","taxonomy","pagination","languages"]

""" For Plugins """
#pagination
PAGINATION_LIMIT = 2
#taxonomy
TAXONOMY_PAGINATION_LIMIT = PAGINATION_LIMIT
#languages
TRANSLATES = {
	"en":{"name":u"English", "text":u"Language", "url":u"http://smalltalks.cc"},
	"zh":{"name":u"简体中文", "text":u"语 言", "url":u"http://cn.smalltalks.cc"}
}
TRANSLATE_REDIRECT = False
#shortcodes
SHORTCODES  = [
    {"pattern":"base_url","replacement":""},
    {"pattern":"uploads","replacement":"/uploads"},
    {"pattern":"image_url","replacement":"/uploads"}
]

ADDITIONAL_METAS = ["nav","link","target","parent","thumbnail"]