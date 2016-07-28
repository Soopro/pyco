# coding=utf-8
from __future__ import absolute_import

from flask import Flask, current_app, request, abort, g, make_response
from flask.json import JSONEncoder

from jinja2 import FileSystemLoader

import sys
import os
import traceback
import argparse

from views import (ContentView,
                   RestMetaView,
                   RestContentView,
                   UploadsView)

from helpers import (load_config,
                     make_json_response)


__version_info__ = ('1', '16', '3')
__version__ = '.'.join(__version_info__)

# parse args
parser = argparse.ArgumentParser(
    description='Options of starting Pyco server.')

parser.add_argument('--restful',
                    dest='restful_mode',
                    action='store_const',
                    const=True,
                    help='Manually start pyco restful mode.')

args, unknown = parser.parse_known_args()

# create app
app = Flask(__name__)
app.version = __version__

load_config(app)

# make importable for plugin folder
sys.path.insert(0, os.path.join(app.config.get("BASE_DIR"),
                                app.config.get("PLUGIN_DIR")))

# init app
app.debug = app.config.get("DEBUG", True)
app.template_folder = os.path.join(app.config.get("THEMES_DIR"),
                                   app.config.get("THEME_NAME"))

app.static_folder = app.config.get("THEMES_DIR")
app.static_url_path = "/{}".format(app.config.get("STATIC_PATH"))
app.restful = args.restful_mode or app.config.get('RESTFUL')


# extend jinja
app.jinja_env.autoescape = False
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
# app.jinja_env.add_extension('jinja2.ext.i18n')
app.jinja_env.add_extension('jinja2.ext.do')
app.jinja_env.add_extension('jinja2.ext.with_')
# app.jinja_env.install_gettext_callables(gettext, ngettext, newstyle=True)


# routes
app.add_url_rule(
    "/",
    defaults={"_": ""},
    view_func=ContentView.as_view("index")
)

app.add_url_rule(
    "/<path:_>",
    view_func=ContentView.as_view("content")
)


app.add_url_rule(
    app.static_url_path + '/<path:filename>',
    view_func=app.send_static_file,
    endpoint='static'
)

app.add_url_rule(
    "/{}/<path:filepath>".format(app.config.get("UPLOADS_DIR")),
    view_func=UploadsView.as_view("uploads")
)


if app.restful:
    app.json_encoder = JSONEncoder

    app.add_url_rule(
        "/restapi/context",
        view_func=RestMetaView.as_view("metas")
    )

    app.add_url_rule(
        "/restapi/contents",
        view_func=RestContentView.as_view("contents")
    )
    app.add_url_rule(
        "/restapi/contents/<type_slug>",
        view_func=RestContentView.as_view("contents")
    )


@app.before_request
def before_request():
    if request.method == "OPTIONS":
        resp = current_app.make_default_options_response()
        return resp

    load_config(current_app)
    if request.path.strip("/") in current_app.config.get('SYS_ICON_LIST'):
        abort(404)

    base_url = current_app.config.get("BASE_URL")
    base_path = current_app.config.get("BASE_PATH")
    uploads_dir = current_app.config.get("UPLOADS_DIR")

    g.curr_base_url = base_url
    g.curr_base_path = base_path
    g.request_path = request.path.replace(base_path, '', 1) or '/'
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
    if current_app.restful:
        return make_json_response(err_html_msg, 500)
    else:
        return make_response(err_html_msg, 500)


if __name__ == "__main__":
    host = app.config.get("HOST")
    port = app.config.get("PORT")

    print "-------------------------------------------------------"
    print "Pyco: {}".format(app.version)
    print "RESTFUL:", bool(app.restful)
    print "-------------------------------------------------------"

    if app.debug:
        debug_msg = "\n".join(["Pyco is running in DEBUG mode !!!",
                               "Jinja2 template folder is about to reload."])
        print(debug_msg)

    app.run(host=host, port=port, debug=True, threaded=True)
