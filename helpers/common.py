# coding=utf-8
from __future__ import absolute_import

from flask import g
import json
import os
import re
from hashlib import sha1
from types import ModuleType

from utils.misc import DottedImmutableDict


def get_app_metas(config):
    theme_meta_file = os.path.join(config.get('THEMES_DIR'),
                                   config.get('THEME_NAME'),
                                   config.get('THEME_META_FILE'))
    theme_meta = open(theme_meta_file)
    try:
        config['THEME_META'] = json.load(theme_meta)
    except Exception as e:
        err_msg = "Load Theme Meta faild: {}".format(str(e))
        raise Exception(err_msg)
    theme_meta.close()

    site_file = os.path.join(config.get('CONTENT_DIR'),
                             config.get('SITE_DATA_FILE'))
    try:
        with open(site_file) as site_data:
            config['SITE'] = json.load(site_data)
            site_meta = config['SITE'].get("meta", {})
            g.curr_app = {
                "locale": site_meta.get("locale", u'en_US')
            }
    except Exception as e:
        err_msg = "Load Site Meta faild: {}".format(str(e))
        raise Exception(err_msg)


def load_plugins(plugins):
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
    return loaded_plugins


def generate_etag(content_file_full_path):
    file_stat = os.stat(content_file_full_path)
    base = "{mtime:0.0f}_{size:d}_{fpath}".format(
        mtime=file_stat.st_mtime,
        size=file_stat.st_size,
        fpath=content_file_full_path
    )

    return sha1(base).hexdigest()


def make_dotted_dict(obj):
    if isinstance(obj, dict):
        return DottedImmutableDict(obj)
    elif isinstance(obj, list):
        new_obj = []
        for i in obj:
            new_obj.append(make_dotted_dict(i))
        return new_obj
    else:
        return obj


def make_redirect_url(url, base_url):
    if not url or not isinstance(url, (str, unicode)):
        return None
    if re.match("^(?:http|ftp)s?://", url):
        return url
    else:
        return "{}/{}".format(base_url, url.strip('/'))
