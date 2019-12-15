# coding=utf-8

DEBUG = True

HOST = '0.0.0.0'
PORT = 5500

PAYLOAD_DIR = 'payload'
BACKUPS_DIR = '_backups'

THEME_NAME = 'default'

BASE_URL = 'http://localhost:5500'
API_URL = 'http://localhost:5500/restapi'
THEME_URL = '{}/static/{}'.format(BASE_URL, THEME_NAME)
UPLOADS_URL = '{}/uploads'.format(BASE_URL)
RES_URL = '{}/res'.format(UPLOADS_URL)

SYS_ICONS = [
    'favicon.ico',
    'apple-touch-icon-precomposed.png',
    'apple-touch-icon.png'
]

CONTENT_QUERY_LIMIT = 3

# markdown
USE_MARKDOWN = False
MARKDOWN_EXTENSIONS = []

# shortcode
SHORTCODE = {
    'uploads': UPLOADS_URL
}

# plugins
PLUGINS = []


# admin
ADMIN_PORT = 5510
ADMIN_BASE_URL = 'http://localhost:5510'
SECRET_KEY = ':~IO#]`lYS)$jx?)O2ON%$G&3w8GA%'
