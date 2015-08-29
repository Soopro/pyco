#coding=utf-8
from __future__ import absolute_import

from flask import (Flask, current_app, request, abort, render_template, g,
                   make_response, redirect, send_from_directory, send_file)

from flask.views import MethodView
from jinja2 import FileSystemLoader

from helpers import (load_config, make_json_response, url_validator,
                     helper_parse_template, helper_translate_template,
                     helper_process_url, sortby)

from collections import defaultdict
from hashlib import sha1
from werkzeug.datastructures import ImmutableDict
from types import ModuleType
from datetime import datetime
from gettext import gettext, ngettext
import sys, os, re, traceback, markdown, json, argparse, yaml

from pyco import BaseView


class EditorTpl(BaseView):
    def get(self, tmpl):
        self.config = current_app.config
        self.load_metas()
        site_meta = self.config.get("SITE",{}).get("meta")
        theme_meta = self.config.get("THEME_META")
        locale = site_meta.get("locale", 'en')
        theme_textdomain = theme_meta.get("textdomain")
        
        theme_folder = current_app.template_folder
        
        tmpl_file = "{}{}".format(tmpl, TPL_FILE_EXT)
        tmpl_path = os.path.join(theme_folder, tmpl_file)
        tmpl_content = helper_parse_template(tmpl_path)
        tmpl_content = helper_translate_template(tmpl_content,
                                                 theme_folder,
                                                 locale,
                                                 theme_textdomain)
        output = {
            "tpl": tmpl_content
        }
        return make_json_response(output)



class EditorView(BaseView):
    def get(self, _):
        # init
        status_code = 200
        is_not_found = False
        run_hook = self.run_hook
        
        #for pass intor hook
        file = {"path": None}
        file_content = {"content": None}
        
        # load
        self.config = current_app.config
        self.load_metas()
        self.load_plugins()
        run_hook("plugins_loaded")

        current_app.debug = self.config.get("DEBUG", True)

        self.init_context()
        
        run_hook("config_loaded", config=self.config)
        
        config = self.config

        self.view_ctx["args"] = {}
        
        # run_hook("request_url", request=request, redirect_to=redirect_to)

        file["path"] = self.get_file_path(request.path)
        # hook before load content
        run_hook("before_load_content", file=file)
        # if not found
        if file["path"] is None:
            is_not_found = True
            status_code = 404
            file["path"] = self.content_not_found_full_path
            if not self.check_file_exists(file["path"]):
                # without not found file
                abort(404)

        # read file content
        if is_not_found:
            run_hook("before_404_load_content", file=file)

        with open(file['path'], "r") as f:
            file_content['content'] = f.read().decode(CHARSET)
        
        if is_not_found:
            run_hook("after_404_load_content", file=file, content=file_content)
        run_hook("after_load_content", file=file, content=file_content)
        
        # parse file content
        tmp_file_content = file_content["content"]
        meta_string, content_string = self.content_splitter(tmp_file_content)

        page_meta = self.parse_page_meta(meta_string)
        page_meta = self.parse_file_attrs(page_meta,
                                          file["path"],
                                          content_string)
        
        redirect_to = {"url": None}

        run_hook("single_page_meta",
                 page_meta=page_meta,
                 redirect_to=redirect_to)


        self.view_ctx["meta"] = page_meta
        
        page_content = dict()

        page_content['content'] = content_string
        run_hook("before_parse_content", content=page_content)
        
        page_content['content'] = self.parse_content(page_content['content'],
                                                     page_meta.get("markdown"))
        run_hook("after_parse_content", content=page_content)
        
        self.view_ctx["content"] = page_content['content']
        
        # menu
        if self.max_mode:
            self.view_ctx["menu"] = self.get_menus()
        
        # taxonomy
        if self.max_mode:
            self.view_ctx["taxonomy"] = self.get_taxonomies()
            self.view_ctx["tax"] = self.view_ctx["taxonomy"]
        
        # content
        pages = self.get_pages()
        self.view_ctx["pages"] = pages
        
        run_hook("get_pages",
                 pages=self.view_ctx["pages"],
                 current_page=self.view_ctx["meta"])
        
        # template
        template = dict()

        template['file'] = self.view_ctx["meta"].get("template")
        
        run_hook("before_render", var=self.view_ctx, template=template)

        # make dotted able
        # for k,v in self.view_ctx.iteritems():
        #     self.view_ctx[k] = helper_make_dotted_dict(v)
        #
        # output = {}
        # output['content'] = render_template(template_file_path,
        #                                     **self.view_ctx)
        # run_hook("after_render", output=output)
        return make_json_response(self.view_ctx)




# create app
app = Flask(__name__)
load_config(app)

# init config
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

PLUGIN_DIR = app.config.get("PLUGIN_DIR")
THEMES_DIR = app.config.get("THEMES_DIR")

TEMPLATE_FILE_EXT = app.config.get("TEMPLATE_FILE_EXT")

DEFAULT_SITE_META_FILE = app.config.get("DEFAULT_SITE_META_FILE")
DEFAULT_THEME_META_FILE = app.config.get("DEFAULT_THEME_META_FILE")

DEFAULT_TEMPLATE = app.config.get("DEFAULT_TEMPLATE")
DEFAULT_DATE_FORMAT = app.config.get("DEFAULT_DATE_FORMAT")

DEFAULT_EXCERPT_LENGTH = app.config.get("DEFAULT_EXCERPT_LENGTH")
DEFAULT_EXCERPT_ELLIPSIS = app.config.get("DEFAULT_EXCERPT_ELLIPSIS")

STATIC_BASE_URL = app.config.get("STATIC_BASE_URL")

UPLOADS_DIR = app.config.get("UPLOADS_DIR")
THUMBNAILS_DIR = app.config.get("THUMBNAILS_DIR")


CONTENT_DIR = app.config.get("CONTENT_DIR")
CONTENT_FILE_EXT = app.config.get("CONTENT_FILE_EXT")

DEFAULT_INDEX_ALIAS = app.config.get("DEFAULT_INDEX_ALIAS")
DEFAULT_404_ALIAS = app.config.get("DEFAULT_404_ALIAS")

INVISIBLE_PAGE_LIST = app.config.get("INVISIBLE_PAGE_LIST")

SYS_ICON_LIST = app.config.get("SYS_ICON_LIST")
CHARSET = app.config.get("CHARSET")

# editor
TPL_FILE_EXT = app.config.get("TPL_FILE_EXT")
EDITOR_BASE_URL = app.config.get("EDITOR_BASE_URL")
EDITOR_DIR = app.config.get("EDITOR_DIR")

# make importable for plugin folder
sys.path.insert(0, os.path.join(BASE_DIR, PLUGIN_DIR))

# init app
app.debug = app.config.get("DEBUG", True)
app.template_folder = os.path.join(THEMES_DIR, app.config.get("THEME_NAME"))
app.static_folder = EDITOR_DIR
app.static_url_path = EDITOR_BASE_URL

# extend jinja
app.jinja_env.add_extension('jinja2.ext.i18n')
app.jinja_env.install_gettext_callables(gettext, ngettext, newstyle=True)


# routes
app.add_url_rule(
    EDITOR_BASE_URL + '/<path:filename>',
    endpoint='static', view_func=app.send_static_file)

app.add_url_rule("/content/<path:_>",
    view_func=EditorView.as_view("editor_content"))

app.add_url_rule("/tpl/<tmpl>",
    view_func=EditorTpl.as_view("editor_tpl"))


@app.before_request
def before_request():
    load_config(current_app)
    if current_app.debug:
        # change template folder
        current_app.template_folder = os.path.join(THEMES_DIR,
                                      current_app.config.get("THEME_NAME"))
        # change reload template folder
        current_app.jinja_env.cache = None
        tpl_folder = current_app.template_folder
        current_app.jinja_loader = FileSystemLoader(tpl_folder)
        # current_app._get_current_object().jinja_loader = FileSystemLoader(current_app.template_folder)


@app.errorhandler(Exception)
def errorhandler(err):
    err_msg = "{}\n{}".format(repr(err), traceback.format_exc())
    current_app.logger.error(err_msg)
    headers = dict()
    headers["Content-Type"] = "application/json"
    output_error = {
        "errcode": 500,
        "errmsg": "Pyco Editor Simulation Error",
        "erraffix": '',
        "request":{
            "request_api": request.path,
            "request_method": request.method,
            "request_body": None,
        }
    }
    return make_response(json.dumps(output_error), 500, headers)


if __name__ == "__main__":
    host = app.config.get("HOST")
    port = app.config.get("EDITOR_PORT")
    app.run(host=host, port=port, debug=True)