#coding=utf-8
from __future__ import absolute_import
import os

DEBUG = True

HOST = '0.0.0.0'
PORT = 5500
RESTFUL = False
EDITOR = False

THEME_NAME = 'dev'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

BASE_URL = "http://localhost:5500"
BASE_PATH = ""

LIBS_URL = "http://libs.soopro.com"

CHARSET = "utf8"

PLUGIN_DIR = "plugins"

THEMES_DIR = "themes"
TEMPLATE_FILE_EXT = ".html"

MAX_MODE_TYPES = ["ws"]

DEFAULT_SITE_META_FILE = "site.json"
DEFAULT_THEME_META_FILE = "config.json"

DEFAULT_TEMPLATE = "index"
DEFAULT_DATE_FORMAT = '%Y-%m-%d'

DEFAULT_EXCERPT_LENGTH = 50
DEFAULT_EXCERPT_ELLIPSIS = "&hellip;"

STATIC_BASE_URL = "/static"

UPLOADS_DIR = "uploads"

CONTENT_DIR = "content"
CONTENT_FILE_EXT = ".md"

DEFAULT_INDEX_SLUG = "index"
DEFAULT_404_SLUG = "error_404"

INVISIBLE_PAGE_LIST = [DEFAULT_404_SLUG]

SHORT_ATTR_KEY = {}

IGNORE_FILES = []

SYS_ICON_LIST = ['favicon.ico',
                 'apple-touch-icon-precomposed.png',
                 'apple-touch-icon.png']

USE_MARKDOWN = False
MARKDOWN_EXTENSIONS = ['gfm']


# plugins
PLUGINS = ["draft",
           "languages",
           "socials",
           "slots",
           "content_types",
           "is",
           "redirect",
           "template",
           "shortcode",
           "jinja_helper"]

""" For Plugins """
