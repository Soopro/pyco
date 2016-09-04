# coding=utf-8
from __future__ import absolute_import

from helpers.common import *
from helpers.restapi import _query, _add_pagination
from utils.request import get_param, get_args
from utils.response import output_json

from helpers.app import helper_record_statistic, helper_get_statistic
from helpers.content import (helper_render_ext_slots,
                             helper_wrap_translates,
                             helper_wrap_socials,
                             helper_wrap_menu,
                             helper_wrap_taxonomy)

@output_json
def app_visit(app_id, file_id=None):
    helper_record_statistic(app_id, file_id)
    return helper_get_statistic(app_id, file_id)


@output_json
def app_visit_status(app_id, file_id):
    return helper_get_statistic(app_id, file_id)


@output_json
def get_view_metas(app_id):
    config = current_app.config
    curr_app = g.curr_app

    theme_meta = curr_app['theme_meta']

    site_meta = curr_app["meta"]
    site_meta['title'] = curr_app["title"]
    site_meta['description'] = curr_app["description"]
    site_meta['slug'] = curr_app['slug']
    site_meta["id"] = curr_app["_id"]
    site_meta["type"] = curr_app['type']

    translates = curr_app['translates']
    locale = curr_app['locale']

    ext_slots = curr_app["slots"]
    for k, v in ext_slots.iteritems():
        ext_slots[k] = helper_render_ext_slots(v, curr_app)

    context = {
        "app_id": curr_app["_id"],
        "site_meta": site_meta,
        "theme_meta": theme_meta,
        "base_url": g.curr_base_url,
        "theme_url": config.get("THEME_URL", u''),
        "libs_url": config.get("LIBS_URL", u''),
        "lang": locale.split('_')[0],
        "locale": locale,
        "translates": helper_wrap_translates(translates, locale),
        "socials": helper_wrap_socials(curr_app['socials']),
        "menu": helper_wrap_menu(curr_app['menus'], base_url),
        "taxonomy": helper_wrap_taxonomy(curr_app['taxonomies']),
        "content_types": curr_app['content_types'],
        "slot": ext_slots
    }
    return context
