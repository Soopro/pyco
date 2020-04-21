# coding=utf-8

import os
import sys
import time

from flask import Flask, current_app, request, make_response, g
from flask.json import JSONEncoder

from core.utils.request import get_remote_addr, get_request_url
from core.utils.response import make_cors_headers
from core.utils.files import ensure_dirs, concat_path
from core.utils.misc import replace_startswith
from core.loaders import (load_config,
                          load_plugins,
                          load_metas,
                          load_modal_pretreat)
from app.blueprints import register_blueprints

from core.models import DBConnection, Configure, Document, Site, Theme, Media

import info


# create app
app = Flask(__name__, static_url_path='/static')
app.version = info.__version__

load_config(app)


app.db = DBConnection(app.config['PAYLOAD_DIR'], load_modal_pretreat(app))
app.db.register([Configure, Document, Site, Theme, Media])

# ensure dirs
ensure_dirs(
    app.config['PAYLOAD_DIR'],
    app.config['BACKUPS_DIR'],
    concat_path(app.config['PAYLOAD_DIR'], Theme.THEMES_DIR),
    concat_path(app.config['PAYLOAD_DIR'], Site.CONTENT_DIR),
    concat_path(app.config['PAYLOAD_DIR'], Media.UPLOADS_DIR)
)


# make importable for plugin folder
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'app', 'plugins'))

# template
app.template_folder = os.path.join(app.config['PAYLOAD_DIR'],
                                   Theme.THEMES_DIR,
                                   app.config.get('THEME_NAME'))

# static
app.static_folder = os.path.join(app.config['PAYLOAD_DIR'],
                                 Theme.THEMES_DIR)

# jinja env
app.jinja_env.autoescape = False
app.jinja_env.finalize = lambda x: '' if callable(x) else x
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.jinja_env.add_extension('jinja2.ext.do')
app.jinja_env.add_extension('jinja2.ext.with_')

# encoder
app.json_encoder = JSONEncoder

# plugins
load_plugins(app)

# register blueprints
register_blueprints(app)


# inject before request handlers
@app.before_request
def app_before_request():
    if current_app.debug:
        g._request_time_start = time.time()

    # cors response
    if request.method == 'OPTIONS':
        resp = current_app.make_default_options_response()
        cors_headers = make_cors_headers()
        resp.headers.extend(cors_headers)
        return resp
    elif request.path.strip('/') in current_app.config.get('SYS_ICONS', []):
        return make_response('', 204)  # for browser default icons
    if request.endpoint == 'uploads.get_uploads':
        return

    configure = app.db.Configure()
    base_url = current_app.config.get('BASE_URL')
    uploads_url = current_app.config.get('UPLOADS_URL')
    theme_url = current_app.config.get('THEME_URL')
    api_url = current_app.config.get('API_URL')
    res_url = current_app.config.get('RES_URL')

    if configure['acc_url']:
        if configure['acc_mode'] == 1:
            # replace base_url
            uploads_url = configure['acc_url']
        elif configure['acc_mode'] == 2:
            acc_url = configure['acc_url']
            # use replace because uploads might not sub as base_url
            uploads_url = replace_startswith(uploads_url, base_url, acc_url)
            theme_url = replace_startswith(theme_url, base_url, acc_url)
            api_url = replace_startswith(api_url, base_url, acc_url)
            res_url = replace_startswith(res_url, base_url, acc_url)
            # replace base_url after all
            base_url = acc_url

    g.curr_app = load_metas(current_app)

    g.request_remote_addr = get_remote_addr()
    g.request_path = request.path

    g.base_url = base_url
    g.uploads_url = uploads_url
    g.theme_url = theme_url
    g.api_url = api_url
    g.res_url = res_url
    g.request_url = get_request_url(g.base_url, g.request_path)

    g.query_map = {}


@app.after_request
def app_after_request(resp):
    if request.endpoint == 'static':
        resp.headers = make_cors_headers(resp.headers.get('Content-Type'))
    return resp


@app.teardown_request
def app_teardown_request(exception=None):
    if current_app.debug:
        print('Request Time:', time.time() - g._request_time_start)


if __name__ == '__main__':

    host = app.config.get('HOST')
    port = app.config.get('PORT')
    debug = app.config.get('DEBUG')

    print("-------------------------------------------------------")
    print('Pyco: {}'.format(app.version))
    print("-------------------------------------------------------")

    if app.debug:
        print('Pyco is running in DEBUG mode !!!')
        print('Jinja2 template folder is about to reload.')

    app.run(host=str(host), port=int(port), debug=bool(debug), threaded=True)
