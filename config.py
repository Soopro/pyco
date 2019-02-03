# coding=utf-8
from __future__ import absolute_import

DEBUG = True

HOST = '0.0.0.0'
PORT = 5500

THEME_NAME = 'default'
STATIC_PATH = 'static'

UPLOADS_DIR = 'uploads'
CONTENT_DIR = 'content'
PLUGIN_DIR = 'plugins'
THEMES_DIR = 'themes'

BASE_URL = 'http://localhost:5500'
API_URL = 'http://localhost:5500/restapi'
THEME_URL = '{}/{}/{}'.format(BASE_URL, STATIC_PATH, THEME_NAME)
UPLOADS_URL = '{}/{}'.format(BASE_URL, UPLOADS_DIR)
RES_URL = '{}/res'.format(UPLOADS_URL)

LANGUAGES_DIR = 'languages'

CONTENT_FILE_EXT = '.md'
TEMPLATE_FILE_EXT = '.html'

SITE_DATA_FILE = 'site.json'
THEME_CONF_FILE = 'config.json'

DEFAULT_TEMPLATE = 'index'
DEFAULT_DATE_FORMAT = '%Y-%m-%d'

DEFAULT_EXCERPT_LENGTH = 600

DEFAULT_CONTENT_TYPE = 'page'

DEFAULT_INDEX_SLUG = 'index'
DEFAULT_SEARCH_SLUG = 'search'
DEFAULT_CATEGORY_SLUG = 'category'
DEFAULT_TAG_SLUG = 'tag'
DEFAULT_404_SLUG = 'error-404'

RESERVED_SLUGS = [
    DEFAULT_INDEX_SLUG,
    DEFAULT_TAG_SLUG,
    DEFAULT_CATEGORY_SLUG,
    DEFAULT_SEARCH_SLUG,
]

USE_MARKDOWN = False
MARKDOWN_EXTENSIONS = ['gfm']

MAXIMUM_QUERY = 60

SORTABLE_FIELD_KEYS = ('date', 'updated')
QUERYABLE_FIELD_KEYS = ('slug', 'parent', 'priority', 'template',
                        'date', 'updated', 'creation')
IMAGE_MEDIA_EXTS = ('jpg', 'jpe', 'jpeg', 'png', 'gif', 'bmp', 'tiff')

SYS_ICON_LIST = (
    'favicon.ico',
    'apple-touch-icon-precomposed.png',
    'apple-touch-icon.png'
)

# plugins
PLUGINS = []
