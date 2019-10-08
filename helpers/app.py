# coding=utf-8

from flask import current_app
from hashlib import sha1
import os
import re


def run_hook(hook_name, **references):
    for plugin_module in current_app.plugins:
        func = plugin_module.__dict__.get(hook_name)
        if callable(func):
            func(**references)
    return


def generate_etag(content_file_full_path):
    file_stat = os.stat(content_file_full_path)
    base = '{mtime:0.0f}_{size:d}_{fpath}'.format(
        mtime=file_stat.st_mtime,
        size=file_stat.st_size,
        fpath=content_file_full_path
    )

    return sha1(base).hexdigest()


def get_theme_path(tmpl_name):
    return '{}{}'.format(tmpl_name,
                         current_app.config.get('TEMPLATE_FILE_EXT'))


def helper_redirect_url(url, base_url):
    if not url or not isinstance(url, str):
        return None
    if re.match('^(?:http|ftp)s?://', url):
        return url
    else:
        return '{}/{}'.format(base_url, url.strip('/'))
