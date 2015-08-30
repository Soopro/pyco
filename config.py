#coding=utf-8
from __future__ import absolute_import
import os

DEBUG = True

HOST = '0.0.0.0'
PORT = 5500
EDITOR_PORT = 5550

THEME_NAME = 'dev'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

BASE_URL = "http://localhost:5500"

CHARSET = "utf8"

PLUGIN_DIR = "plugins"

THEMES_DIR = "themes"
TEMPLATE_FILE_EXT = ".html"
TPL_FILE_EXT = ".tpl"

MAX_MODE_TYPES = ["ws"]

DEFAULT_SITE_META_FILE = "site.json"
DEFAULT_THEME_META_FILE = "config.json"

DEFAULT_TEMPLATE = "index"
DEFAULT_DATE_FORMAT = '%Y-%m-%d'

DEFAULT_EXCERPT_LENGTH = 50
DEFAULT_EXCERPT_ELLIPSIS = "&hellip;"

STATIC_BASE_URL = "/static"

UPLOADS_DIR = "uploads"
THUMBNAILS_DIR = "thumbnails"

CONTENT_DIR = "content"
CONTENT_FILE_EXT = ".md"

DEFAULT_INDEX_ALIAS = "index"
DEFAULT_404_ALIAS = "error_404"

INVISIBLE_PAGE_LIST = [DEFAULT_404_ALIAS]
CONTENT_QUERY_FIELDS = ['alias', 'content_type', 
                        'priority', 'locked' 'updated']
                        
IGNORE_FILES = []

SYS_ICON_LIST = ['favicon.ico', 
                 'apple-touch-icon-precomposed.png',
                 'apple-touch-icon.png']

PLUGINS = ["draft",
           "languages",
           "content_types",
           "redirect",
           "template",
           "marker",
           "jinja_helper"]

""" For Plugins """
