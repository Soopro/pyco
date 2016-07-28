# coding=utf-8
from __future__ import absolute_import
import re


RE_UPLOADS_DIR = re.compile(r"\[\%uploads\%\]", re.IGNORECASE)
RE_THEME_URL = re.compile(r"\[\%theme\%\]", re.IGNORECASE)

_CONFIG = {}


def config_loaded(config):
    global _CONFIG
    _CONFIG = config
    return


def before_read_page_meta(meta_string):
    # pre process the content for data convert safety.
    meta_string['meta'] = replace(meta_string['meta'])
    return


def before_render(var, template):
    # it is possible generated a new shortcode while in the process.
    # do it before render is for template render safety.
    for key in var:
        var[key] = parser_replace(var[key])
    return


def after_render(output):
    # finally make sure everthing processed.
    output['content'] = replace(output['content'])
    return


# custom functions
def replace(content):
    # uploads
    uploads_dir = "{}/{}".format(_CONFIG["BASE_URL"],
                                 _CONFIG["UPLOADS_DIR"])
    content = re.sub(RE_UPLOADS_DIR, unicode(uploads_dir), content)

    # theme
    theme_url = "{}/{}/{}".format(_CONFIG["BASE_URL"],
                                  _CONFIG["STATIC_PATH"],
                                  _CONFIG["THEME_NAME"])
    content = re.sub(RE_THEME_URL, unicode(theme_url), content)

    return content


def parser_replace(item):
    if isinstance(item, (dict, list)):
        obj = item if isinstance(item, dict) else xrange(len(item))
        for i in obj:
            item[i] = parser_replace(item[i])
    elif isinstance(item, (str, unicode)):
        item = replace(item)
    return item
