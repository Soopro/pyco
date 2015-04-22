#coding=utf-8
from __future__ import absolute_import

DEBUG = True

HOST = '0.0.0.0'
PORT = 5500

THEME_NAME = 'dev'

BASE_URL = "http://localhost:5500/"

CHARSET = "utf8"

PLUGIN_DIR = "plugins/"

THEMES_DIR = "themes/"
TEMPLATE_FILE_EXT = ".html"
TPL_FILE_EXT = ".tpl"

DEFAULT_SITE_META_FILE = "site.json"
DEFAULT_THEME_META_FILE = "config.json"

DEFAULT_TEMPLATE = "index"
DEFAULT_DATE_FORMAT = '%Y-%m-%d'

DEFAULT_EXCERPT_LENGTH = 50
DEFAULT_EXCERPT_ELLIPSIS = "&hellip;"

STATIC_BASE_URL = "/static"
STATIC_HOST = BASE_URL+"static/"
LIBS_HOST = "http://libs.soopro.com"

UPLOADS_DIR = "uploads"
THUMBNAILS_DIR = "thumbnails"

EDITOR_DIR = "editor"
EDITOR_INDEX = "index.html"

CONTENT_DIR = "content"
CONTENT_FILE_EXT = ".md"

DEFAULT_INDEX_ALIAS = "index"
DEFAULT_404_ALIAS = "error_404"

INVISIBLE_PAGE_LIST = [DEFAULT_404_ALIAS]

IGNORE_FILES = []


PLUGINS = ["autometas",
           "draft",
           "languages",
           "content_types",
           "redirect",
           "marker",
           "jinja_helper"]

""" For Plugins """
