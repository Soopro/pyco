# coding=utf-8
from __future__ import absolute_import

from flask import (Blueprint, request, current_app, g, make_response)
from jinja2 import FileSystemLoader
import os
from utils.misc import route_inject
from helpers.app import get_app_metas

from .helpers.jinja import (filter_thumbnail,
                            filter_date_formatted,
                            filter_url,
                            filter_path,
                            filter_args)
from .routes import url


SYS_ICON_LIST = ['favicon.ico',
                 'apple-touch-icon-precomposed.png',
                 'apple-touch-icon.png']

bp_name = "tradition"

blueprint = Blueprint(bp_name, __name__)

route_inject(blueprint, url)


@blueprint.before_app_first_request
def before_first_request():
    current_app.jinja_env.filters['thumbnail'] = filter_thumbnail
    current_app.jinja_env.filters['url'] = filter_url
    current_app.jinja_env.filters['path'] = filter_path
    current_app.jinja_env.filters['args'] = filter_args
    current_app.jinja_env.filters['date_formatted'] = filter_date_formatted


@blueprint.before_request
def before_request():
    if request.method == "OPTIONS":
        return current_app.make_default_options_response()
    elif request.path.strip("/") in SYS_ICON_LIST:
        return make_response('', 204)  # for browser default icons

    base_url = current_app.config.get("BASE_URL")
    uploads_dir = current_app.config.get("UPLOADS_DIR")

    g.curr_app = get_app_metas()
    g.curr_base_url = base_url
    g.request_path = request.path
    g.request_url = "{}/{}".format(g.curr_base_url, g.request_path)
    g.uploads_url = "{}/{}".format(base_url, uploads_dir)

    if current_app.debug:
        # change template folder
        themes_dir = current_app.config.get("THEMES_DIR")
        theme_name = current_app.config.get("THEME_NAME")
        current_app.template_folder = os.path.join(themes_dir, theme_name)
        # change reload template folder
        current_app.jinja_env.cache = None
        tpl_folder = current_app.template_folder
        current_app.jinja_loader = FileSystemLoader(tpl_folder)
