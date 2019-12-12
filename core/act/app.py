# coding=utf-8

from flask import current_app
import re


def run_hook(hook_name, **references):
    for plugin_module in current_app.plugins:
        func = plugin_module.__dict__.get(hook_name)
        if callable(func):
            func(**references)
    return


def get_theme_path(tmpl_name, ext='.html'):
    return '{}{}'.format(tmpl_name, ext)


def get_redirect_url(url, base_url):
    if not url or not isinstance(url, str):
        return None
    if re.match('^(?:http|ftp)s?://', url):
        return url
    else:
        return '{}/{}'.format(base_url, url.strip('/'))
