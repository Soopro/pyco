# coding=utf-8
from __future__ import absolute_import

DEBUG = True

HOST = '0.0.0.0'
PORT = 5500

THEME_NAME = 'default'
STATIC_PATH = 'static'

BASE_URL = 'http://localhost:5500'
API_BASEURL = 'http://localhost:5500/restapi'
THEME_URL = '{}/{}/{}'.format(BASE_URL, STATIC_PATH, THEME_NAME)

UPLOADS_DIR = 'uploads'
CONTENT_DIR = 'content'
PLUGIN_DIR = 'plugins'
THEMES_DIR = 'themes'

LANGUAGES_DIR = 'languages'

CONTENT_FILE_EXT = '.md'
TEMPLATE_FILE_EXT = '.html'

SITE_DATA_FILE = 'site.json'
THEME_CONF_FILE = 'config.json'

DEFAULT_TEMPLATE = 'index'
DEFAULT_DATE_FORMAT = '%Y-%m-%d'

DEFAULT_EXCERPT_LENGTH = 162
DEFAULT_EXCERPT_ELLIPSIS = '&hellip;'

DEFAULT_INDEX_SLUG = 'index'
DEFAULT_404_SLUG = 'error-404'
DEFAULT_SEARCH_SLUG = 'search'
DEFAULT_TAXONOMY_SLUG = 'category'
DEFAULT_TAG_SLUG = 'tag'

RESERVED_SLUGS = [
    DEFAULT_INDEX_SLUG,
    DEFAULT_404_SLUG,
    DEFAULT_SEARCH_SLUG,
    DEFAULT_TAG_SLUG,
]

USE_MARKDOWN = False
MARKDOWN_EXTENSIONS = ['gfm']

MAXIMUM_QUERY = 60

FIELD_KEY_ALIASES = {'type': 'content_type'}
SORTABLE_FIELD_KEYS = ('date', 'updated')
QUERYABLE_FIELD_KEYS = ('slug', 'content_type', 'priority', 'parent',
                        'date', 'creation', 'updated',
                        'template', 'tags')
IMAGE_MEDIA_EXTS = ('jpg', 'jpe', 'jpeg', 'png', 'gif', 'bmp', 'tiff')

# plugins
PLUGINS = []
