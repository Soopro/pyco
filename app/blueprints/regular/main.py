# coding=utf-8

from flask import Blueprint, current_app, make_response, request
import traceback

from core.utils.misc import route_inject

from .helpers.jinja import (filter_thumbnail,
                            filter_timestamp,
                            filter_date_formatted,
                            filter_background_image,
                            filter_column_offset,
                            filter_active,
                            filter_url,
                            filter_path,
                            filter_args,
                            filter_price)
from .routes import urlpatterns

bp_name = 'regular'

blueprint = Blueprint(bp_name, __name__)
route_inject(blueprint, urlpatterns)


@blueprint.before_app_first_request
def before_first_request():
    current_app.jinja_env.filters['thumbnail'] = filter_thumbnail
    current_app.jinja_env.filters['t'] = filter_timestamp
    current_app.jinja_env.filters['url'] = filter_url
    current_app.jinja_env.filters['path'] = filter_path
    current_app.jinja_env.filters['active'] = filter_active
    current_app.jinja_env.filters['args'] = filter_args
    current_app.jinja_env.filters['date_formatted'] = filter_date_formatted
    current_app.jinja_env.filters['bg_img'] = filter_background_image
    current_app.jinja_env.filters['col_offset'] = filter_column_offset
    current_app.jinja_env.filters['price'] = filter_price


@blueprint.before_request
def before_request():
    if current_app.debug:
        # clear jinja cache for instance reload pages.
        current_app.jinja_env.cache = None

    if request.path.strip('/') in current_app.config.get('SYS_ICONS', []):
        # for browser default icons
        return make_response('', 204)

    # view args
    request.view_args.setdefault('content_type_slug',
                                 current_app.db.Document.STATIC_TYPE)
    request.view_args.setdefault('file_slug',
                                 current_app.db.Document.INDEX_SLUG)


@blueprint.errorhandler(Exception)
def errorhandler(err):
    err_log = '{}\n{}'.format(repr(err), traceback.format_exc())
    err_title = '<h1>{}</h1>'.format(type(err).__name__)
    err_msg = '<h2>{}</h2>'.format(str(err))
    err_tb = '<p><small>{}</small></p>'.format(err_log)
    err_html = '{}{}{}'.format(err_title, err_msg, err_tb)
    current_app.logger.error(err_log)
    return make_response(err_html, 500)
