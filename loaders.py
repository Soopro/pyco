# coding=utf8
from __future__ import absolute_import

from flask import current_app, make_response, send_from_directory
from utils.response import make_cors_headers
from types import ModuleType
import os
import mimetypes


def load_config(app, config_name="config.py"):
    app.config.from_pyfile(config_name)
    app.config.setdefault("DEBUG", False)
    app.config.setdefault("BASE_URL", "/")
    app.config.setdefault("BASE_PATH", "")
    app.config.setdefault("LIBS_URL", "http://libs.soopro.com")
    app.config.setdefault("PLUGINS", [])
    app.config.setdefault("INVISIBLE_PAGE_LIST", [])
    app.config.setdefault("THEME_NAME", "default")
    app.config.setdefault("HOST", "0.0.0.0")
    app.config.setdefault("PORT", 5500)
    app.config.setdefault("SITE", {})
    app.config.setdefault("THEME_META", {})
    app.config.setdefault("CHARSET", "utf8")
    app.config.setdefault("SYS_ICON_LIST", [])

    app.config.setdefault("PLUGIN_DIR", "plugins")
    app.config.setdefault("THEMES_DIR", "themes")
    app.config.setdefault("TEMPLATE_FILE_EXT", ".html")
    app.config.setdefault("TPL_FILE_EXT", ".tpl")

    app.config.setdefault("SITE_DATA_FILE", "site.json")
    app.config.setdefault("THEME_META_FILE", "config.json")

    app.config.setdefault("DEFAULT_TEMPLATE", "index")

    app.config.setdefault("DEFAULT_DATE_FORMAT", "%Y-%m-%d")
    app.config.setdefault("DEFAULT_EXCERPT_LENGTH", 162)
    app.config.setdefault("DEFAULT_EXCERPT_ELLIPSIS", "&hellip;")

    app.config.setdefault("STATIC_PATH", "static")
    app.config.setdefault("UPLOADS_DIR", "uploads")
    app.config.setdefault("CONTENT_DIR", "content")
    app.config.setdefault("CONTENT_FILE_EXT", ".md")
    app.config.setdefault("DEFAULT_INDEX_SLUG", "index")
    app.config.setdefault("DEFAULT_404_SLUG", "error_404")


def load_plugins(app):
    plugins = app.config.get("PLUGINS")
    loaded_plugins = []
    for module_or_module_name in plugins:
        if type(module_or_module_name) is ModuleType:
            loaded_plugins.append(module_or_module_name)
        elif isinstance(module_or_module_name, basestring):
            try:
                module = __import__(module_or_module_name)
            except ImportError as err:
                raise err
            loaded_plugins.append(module)
    app.plugins = loaded_plugins


def load_uploads(filepath):
    filename = os.path.basename(filepath)
    try:
        mime_type = mimetypes.guess_type(filename)[0]
    except:
        mime_type = 'text'

    uploads_dir = current_app.config.get("UPLOADS_DIR")
    send_file = send_from_directory(uploads_dir, filepath)
    response = make_response(send_file)
    response.headers = make_cors_headers(mime_type)
    return response
