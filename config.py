# coding=utf-8

DEBUG = True

HOST = '0.0.0.0'
PORT = 5500

THEMES_DIR = 'themes'
THEME_NAME = 'default'
STATIC_PATH = 'static'

BASE_URL = 'http://localhost:5500'
API_URL = 'http://localhost:5500/restapi'
THEME_URL = '{}/{}/{}'.format(BASE_URL, STATIC_PATH, THEME_NAME)
UPLOADS_URL = '{}/uploads'.format(BASE_URL)
RES_URL = '{}/res'.format(UPLOADS_URL)

SYS_ICONS = [
    'favicon.ico',
    'apple-touch-icon-precomposed.png',
    'apple-touch-icon.png'
]

# markdown
USE_MARKDOWN = False
MARKDOWN_EXTENSIONS = []


# plugins
PLUGINS = ['default']


# admin
ADMIN_PORT = 5510
ADMIN_BASE_URL = 'http://localhost:5510'
SECRET_KEY = ':~IO#]`lYS)$jx?)O2ON%$G&3w8GA%'
