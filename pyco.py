# coding=utf-8
from __future__ import absolute_import

import os
import sys
import traceback

from flask import Flask, current_app, request
from flask.json import JSONEncoder

from utils.misc import route_inject
from utils.response import make_json_response, make_cors_headers

from routes import urlpatterns
from loaders import load_config, load_plugins
from blueprints import register_blueprints


__version_info__ = ('2', '0', '3')
__version__ = '.'.join(__version_info__)


# create app
app = Flask(__name__)
app.version = __version__

load_config(app)

# make importable for plugin folder
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, app.config.get("PLUGIN_DIR")))

# init app
app.debug = app.config.get("DEBUG", True)
app.template_folder = os.path.join(app.config.get("THEMES_DIR"),
                                   app.config.get("THEME_NAME"))

app.static_folder = app.config.get("THEMES_DIR")
app.static_url_path = "/{}".format(app.config.get("STATIC_PATH"))

# jinja env
app.jinja_env.autoescape = False
app.jinja_env.finalize = lambda x: '' if hasattr(x, '__call__') else x
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
# app.jinja_env.add_extension('jinja2.ext.i18n')
app.jinja_env.add_extension('jinja2.ext.do')
app.jinja_env.add_extension('jinja2.ext.with_')
# app.jinja_env.install_gettext_callables(gettext, ngettext, newstyle=True)

app.json_encoder = JSONEncoder

# config
load_config(app)
# plugins
load_plugins(app)

# register blueprints
register_blueprints(app)

# static
app.add_url_rule(
    app.static_url_path + '/<path:filename>',
    view_func=app.send_static_file,
    endpoint='static'
)
# uplaods
app.add_url_rule(
    "/{}/<path:filepath>".format(app.config.get('UPLOADS_DIR')),
    view_func=load_uploads,
    methods=['GET']
)


@app.before_request
def app_before_request():
    # cors response
    if request.method == "OPTIONS":
        resp = current_app.make_default_options_response()
        cors_headers = make_cors_headers()
        resp.headers.extend(cors_headers)
        return resp


@app.errorhandler(Exception)
def errorhandler(err):
    curr_file = ''
    if 'current_file' in dir(err):
        curr_file = err.current_file
    err_msg = "{}: {}\n{}".format(repr(err),
                                  curr_file,
                                  traceback.format_exc())
    err_html_msg = "<h1>{}: {}</h1><p>{}</p>".format(repr(err),
                                                     curr_file,
                                                     traceback.format_exc())
    current_app.logger.error(err_msg)
    return make_json_response(err_html_msg, 500)


if __name__ == "__main__":
    host = app.config.get("HOST")
    port = app.config.get("PORT")

    print "-------------------------------------------------------"
    print "Pyco: {}".format(app.version)
    print "-------------------------------------------------------"

    if app.debug:
        debug_msg = "\n".join(["Pyco is running in DEBUG mode !!!",
                               "Jinja2 template folder is about to reload."])
        print(debug_msg)

    app.run(host=host, port=port, debug=True, threaded=True)
