# coding=utf-8
from __future__ import absolute_import

from flask import current_app
import os
import re
from hashlib import sha1
from utils.validators import url_validator


def run_hook(hook_name, **references):
    for plugin_module in current_app.plugins:
        func = plugin_module.__dict__.get(hook_name)
        if callable(func):
            func(**references)
    return


def generate_etag(content_file_full_path):
    file_stat = os.stat(content_file_full_path)
    base = "{mtime:0.0f}_{size:d}_{fpath}".format(
        mtime=file_stat.st_mtime,
        size=file_stat.st_size,
        fpath=content_file_full_path
    )

    return sha1(base).hexdigest()


def helper_redirect_url(url, base_url):
    if not url or not isinstance(url, (str, unicode)):
        return None
    if re.match("^(?:http|ftp)s?://", url):
        return url
    else:
        return "{}/{}".format(base_url, url.strip('/'))


# statistic
def helper_get_statistic(app_id, page_id=None):
    sa = {
        'pv': 0,
        'vs': 0,
        'uv': 0,
        'ip': 0,
    }
    if page_id:
        sa['page'] = 0

    return sa


# menus
def helper_wrap_menu(menus, base_url):
    if not menus:
        return {}

    def process_menu_url(menu):
        for item in menu:
            link = item.get("link", "")
            if not link or url_validator(link):
                item["url"] = link
            elif link.startswith('/'):
                item["url"] = "{}/{}".format(base_url, link.strip('/'))
            else:
                item["url"] = link.rstrip('/')
            item["nodes"] = process_menu_url(item.get("nodes", []))
        return menu

    menu_dict = {}
    for menu in menus:
        nodes = menu.get("nodes", [])
        nodes = process_menu_url(nodes)
        menu_dict[menu.get("slug")] = nodes

    return menu_dict


# socials
def helper_wrap_socials(socials):
    """ socials json sample
    {
       "facebook":{
           "name":"Facebook",
           "url":"http://....",
           "code":"..."
       },
       "twitter":{
           "name":"Twitter",
           "url":"http://....",
           "code":"..."
       }
    }
    """
    if not socials:
        return []

    social_list = []

    if isinstance(socials, list):
        # directly append if is list
        social_list = [social for social in socials if social.get('key')]

    elif isinstance(socials, dict):
        # change to list if is dict
        def _make_key(k, v):
            v.update({"key": k})
            return v
        social_list = [_make_key(k, v) for k, v in socials.iteritems()]

    return social_list


# translates
def helper_wrap_translates(translates, locale):
    """ translates json sample
    {
       "zh_CN":{"name":"汉语","url":"http://....."},
       "en_US":{"name":"English","url":"http://....."}
    }
    """
    if not translates:
        return []

    trans_list = []
    lang = locale.split('_')[0]

    if isinstance(translates, list):
        # directly append if is list
        trans_list = [trans for trans in translates if trans.get('key')]

    elif isinstance(translates, dict):
        # change to list if is dict
        def _make_key(k, v):
            v.update({"key": k})
            return v
        trans_list = [_make_key(k, v) for k, v in translates.iteritems()]

    for trans in trans_list:
        trans_key = trans['key'].lower()
        if trans_key == locale.lower() or trans_key == lang.lower():
            trans["active"] = True

    return trans_list
