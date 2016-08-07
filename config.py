# coding=utf-8
from __future__ import absolute_import
import os

DEBUG = True

HOST = '0.0.0.0'
PORT = 5500
RESTFUL = False
EDITOR = False

THEME_NAME = 'default'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

BASE_URL = "http://localhost:5500"
BASE_PATH = ""

API_URL = "http://api.soopro.io"
LIBS_URL = "http://libs.soopro.io"

CHARSET = "utf8"

PLUGIN_DIR = "plugins"

THEMES_DIR = "themes"
TEMPLATE_FILE_EXT = ".html"

MAX_MODE_TYPES = ["ws"]

DEFAULT_SITE_META_FILE = "site.json"
DEFAULT_THEME_META_FILE = "config.json"

DEFAULT_TEMPLATE = "index"
DEFAULT_DATE_FORMAT = '%Y-%m-%d'

DEFAULT_EXCERPT_LENGTH = 162
DEFAULT_EXCERPT_ELLIPSIS = "&hellip;"

STATIC_PATH = "static"

UPLOADS_DIR = "uploads"

CONTENT_DIR = "content"
CONTENT_FILE_EXT = ".md"

DEFAULT_INDEX_SLUG = "index"
DEFAULT_404_SLUG = "error_404"
DEFAULT_SEARCH_SLUG = "search"
DEFAULT_TAXONOMY_SLUG = "taxonomy"
DEFAULT_TAG_SLUG = "tag"

INVISIBLE_SLUGS = [
    DEFAULT_INDEX_SLUG,
    DEFAULT_404_SLUG,
    DEFAULT_SEARCH_SLUG,
    DEFAULT_TAXONOMY_SLUG,
    DEFAULT_TAG_SLUG,
]
SHORT_ATTR_KEY = {}

IGNORE_FILES = []

SYS_ICON_LIST = ['favicon.ico',
                 'apple-touch-icon-precomposed.png',
                 'apple-touch-icon.png']

USE_MARKDOWN = False
MARKDOWN_EXTENSIONS = ['gfm']

MAXIMUM_QUERY = 60

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
