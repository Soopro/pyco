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
        self.load_metas()
        config = self.config
        site_meta = config.get("SITE",{}).get("meta")
        theme_meta = config.get("THEME_META")
        locale = site_meta.get("locale", 'en')
        theme_textdomain = theme_meta.get("textdomain")
        
        theme_folder = current_app.template_folder
        
        tmpl_file = "{}{}".format(tmpl, config.get('TPL_FILE_EXT'))
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
    def get_data(self):
        # init
        status_code = 200
        is_not_found = False
        run_hook = self.run_hook
        
        #for pass intor hook
        file = {"path": None}
        file_content = {"content": None}
        
        # load
        config = self.config
        self.load_metas()
        self.load_plugins(config.get("PLUGINS"))
        run_hook("plugins_loaded")

        current_app.debug = self.config.get("DEBUG", True)

        self.init_context()
        
        run_hook("config_loaded", config=self.config)
        
        base_url = config.get("BASE_URL")
        charset = config.get('CHARSET')
        
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
            file_content['content'] = f.read().decode(charset)
        
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
        
        return self.view_ctx
        
    def get(self, _):
        return make_json_response(self.get_data())

class EditorQuery(EditorView):
    def get(self, _):
        req = request.json
        query_fields = self.config.get('CONTENT_QUERY_FIELDS')
        
        params_fields = req.get('query_fields', {})
        params_attrs = req.get('query_metas', {})
        params_length = req.get('query_length', 12)
        params_sortby = req.get('query_sortby', ['updated'])
        
        raw_data = self.get_data()
        pages = raw_data.get('pages', [])
        
        results=[]
        for page in pages:
            for k, v in params_fields.iteritems():
                if k not in query_fields:
                    continue
                if k not in page and page[k] != v:
                    continue
            for k, v in params_attrs.iteritems():
                if k not in page and (v in ['*', ''] or page[k] != v):
                    continue 

            results.append(page)
        
        # sortby
        sort_desc = True
        sort_keys = ['priority'] + [key for key in params_sortby 
                                    if isinstance(key, (str, unicode))]
        results = sortby(results, sort_keys, reverse=True)
        results = results[0:params_length]
        
        output = {
            "results": results
        }
        return make_json_response(output)

# create app
app = Flask(__name__)
load_config(app)

# make importable for plugin folder
sys.path.insert(0, os.path.join(app.config.get("BASE_DIR"),
                                app.config.get("PLUGIN_DIR")))

# init app
app.editor = True
app.debug = app.config.get("DEBUG", True)
app.template_folder = os.path.join(app.config.get("THEMES_DIR"),
                                   app.config.get("THEME_NAME"))

app.static_folder = app.config.get("THEMES_DIR")
app.static_url_path = app.config.get("STATIC_BASE_URL")

# extend jinja
app.jinja_env.add_extension('jinja2.ext.i18n')
app.jinja_env.install_gettext_callables(gettext, ngettext, newstyle=True)


# routes
app.add_url_rule(
    app.static_url_path + '/<path:filename>',
    endpoint='static', view_func=app.send_static_file)

app.add_url_rule("/content/<path:_>",
    view_func=EditorView.as_view("editor_content"))

app.add_url_rule("/tpl/<tmpl>",
    view_func=EditorTpl.as_view("editor_tpl"))


@app.before_request
def before_request():
    load_config(current_app)
    if current_app.debug:
        themes_dir = current_app.config.get("THEMES_DIR")
        theme_name = current_app.config.get("THEME_NAME")
        current_app.template_folder = os.path.join(themes_dir, theme_name)
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