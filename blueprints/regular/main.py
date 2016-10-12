# coding=utf-8
from __future__ import absolute_import

from flask import Blueprint, current_app, make_response
from jinja2 import FileSystemLoader
import traceback
import os
from utils.misc import route_inject

from .helpers.jinja import (filter_thumbnail,
                            filter_date_formatted,
                            filter_background_image,
                            filter_column_offset,
                            filter_url,
                            filter_path,
                            filter_args)
from .routes import urlpatterns

bp_name = "regular"

blueprint = Blueprint(bp_name, __name__)
route_inject(blueprint, urlpatterns)


@blueprint.before_app_first_request
def before_first_request():
    current_app.jinja_env.filters['thumbnail'] = filter_thumbnail
    current_app.jinja_env.filters['url'] = filter_url
    current_app.jinja_env.filters['path'] = filter_path
    current_app.jinja_env.filters['args'] = filter_args
    current_app.jinja_env.filters['date_formatted'] = filter_date_formatted
    current_app.jinja_env.filters['bg_img'] = filter_background_image
    current_app.jinja_env.filters['col_offset'] = filter_column_offset


@blueprint.before_request
def before_request():
    if current_app.debug:
        # change template folder
        themes_dir = current_app.config.get("THEMES_DIR")
        theme_name = current_app.config.get("THEME_NAME")
        current_app.template_folder = os.path.join(themes_dir, theme_name)
        # change reload template folder
        current_app.jinja_env.cache = None
        tpl_folder = current_app.template_folder
        current_app.jinja_loader = FileSystemLoader(tpl_folder)


@blueprint.errorhandler(Exception)
def errorhandler(err):
    err_msg = "{}\n{}".format(repr(err), traceback.format_exc())
    err_html_msg = "<h1>{}</h1><p>{}</p>".format(repr(err), str(err))
    current_app.logger.error(err_msg)
    return make_response(err_html_msg, 579)
