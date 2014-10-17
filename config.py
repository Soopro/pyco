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

THEME_NAME = "default"
PLUGINS = ["pagination","content_types"]

# for pagination plugin
PAGINATION_LIMIT = 10