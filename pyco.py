#coding=utf-8
from __future__ import absolute_import

PLUGIN_DIR = "plugins/"

THEME_DIR = "theme/"
TEMPLATE_FILE_EXT = ".html"
DEFAULT_INDEX_TMPL_NAME = "index"
DEFAULT_POST_TMPL_NAME = "post"

STATIC_DIR = "static/"
STATIC_BASE_URL = "/static"

CONTENT_DIR = "content/"
CONTENT_FILE_EXT = ".md"
CONTENT_DEFAULT_FILENAME = "index"
CONTENT_NOT_FOUND_FILENAME = "404"

CHARSET = "utf8"

import sys
sys.path.insert(0, PLUGIN_DIR)

from flask import Flask, current_app, request, abort, render_template, make_response
from flask.views import MethodView
import os
import re
from helpers import load_config, make_content_response
from collections import defaultdict
from hashlib import sha1
from werkzeug.datastructures import ImmutableDict
from types import ModuleType

import misaka
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter


class BleepRenderer(misaka.HtmlRenderer, misaka.SmartyPants):
    @staticmethod
    def block_code(text, lang):
        if not lang:
            return '\n<pre><code>%s</code></pre>\n' % text.strip()
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = HtmlFormatter(style="vim", title="%s code" % lang, cssclass="codehilite")
        return highlight(text, lexer, formatter)


class BaseView(MethodView):
    def __init__(self):
        super(BaseView, self).__init__()
        self.plugins = []
        self.config = current_app.config
        self.view_ctx = dict()
        self.view_ctx["tmp"] = dict()
        self.ext_ctx = dict()
        return

    def load_plugins(self):
        loaded_plugins = []
        plugins = self.config.get("PLUGINS")
        for module_or_module_name in plugins:
            if type(module_or_module_name) is ModuleType:
                loaded_plugins.append(module_or_module_name)
            elif isinstance(module_or_module_name, basestring):
                try:
                    module = __import__(module_or_module_name)
                except ImportError:
                    continue
                loaded_plugins.append(module)
        self.plugins = loaded_plugins
        return

    # common funcs
    def get_file_path(self, url):
        base_path = os.path.join(CONTENT_DIR, url[1:]).rstrip("/")

        file_name = "{}{}".format(base_path, CONTENT_FILE_EXT)
        if self.check_file_exists(file_name):
            return file_name

        file_name = os.path.join(base_path, "{}{}".format(CONTENT_DEFAULT_FILENAME, CONTENT_FILE_EXT))
        if self.check_file_exists(file_name):
            return file_name
        return None

    @staticmethod
    def check_file_exists(file_full_path):
        return os.path.isfile(file_full_path)

    # content
    @property
    def content_not_found_relative_path(self):
        return "{}{}".format(CONTENT_NOT_FOUND_FILENAME, CONTENT_FILE_EXT)

    @property
    def content_not_found_full_path(self):
        return os.path.join(CONTENT_DIR, self.content_not_found_relative_path)

    @property
    def content_ignore_files(self):
        base_files = [self.content_not_found_relative_path]
        base_files.extend(current_app.config.get("IGNORE_FILES"))
        return base_files

    @staticmethod
    def content_splitter(file_content):
        pattern = r"(\n)*/\*(\n)*(?P<meta>(.*\n)*)\*/(?P<content>(.*(\n)?)*)"
        re_pattern = re.compile(pattern)
        m = re_pattern.match(file_content)
        if m is None:
            return "", ""
        return m.group("meta"), m.group("content")

    def parse_file_meta(self, meta_string):
        headers = dict()
        self.run_hook("before_read_file_meta")
        for line in meta_string.split("\n"):
            kv_pair = line.split(":", 1)
            if len(kv_pair) == 2:
                headers[kv_pair[0].lower()] = kv_pair[1].strip()
        return headers

    @staticmethod
    def parse_content(content_string):
        extensions = misaka.EXT_NO_INTRA_EMPHASIS | misaka.EXT_FENCED_CODE | misaka.EXT_AUTOLINK | \
            misaka.EXT_LAX_HTML_BLOCKS | misaka.EXT_TABLES
        flags = misaka.HTML_TOC | misaka.HTML_USE_XHTML | misaka.HTML_HARD_WRAP
        render = BleepRenderer(flags=flags)
        md = misaka.Markdown(render, extensions=extensions)
        return md.render(content_string)

    # cache
    @staticmethod
    def generate_etag(content_file_full_path):
        file_stat = os.stat(content_file_full_path)
        base = "{mtime:0.0f}_{size:d}_{fpath}".format(mtime=file_stat.st_mtime, size=file_stat.st_size,
                                                      fpath=content_file_full_path)
        return sha1(base).hexdigest()

    # pages
    @staticmethod
    def get_files(base_dir, ext):
        all_files = []
        for root, directory, files in os.walk(base_dir):
            file_full_paths = [os.path.join(root, f) for f in filter(lambda x: x.endswith(ext), files)]
            all_files.extend(file_full_paths)
        return all_files

    def get_pages(self, sort_key="title", reverse=False):
        files = self.get_files(CONTENT_DIR, CONTENT_FILE_EXT)
        file_data_list = []
        for f in files:
            relative_path = f.split(CONTENT_DIR, 1)[1]
            if relative_path.startswith("~") \
                    or relative_path.startswith("#") \
                    or relative_path in self.content_ignore_files:
                continue
            with open(f, "r") as fh:
                file_content = fh.read().decode(CHARSET)
            meta_string, content_string = self.content_splitter(file_content)
            meta = self.parse_file_meta(meta_string)
            data = dict()
            # generate request url
            if relative_path.endswith(CONTENT_FILE_EXT):
                relative_path = relative_path[:-len(CONTENT_FILE_EXT)]

            if relative_path.endswith("index"):
                relative_path = relative_path[:-5]

            url = "/{}".format(relative_path)

            data["path"] = f
            data["title"] = meta.get("title", "")
            data["url"] = url
            data["author"] = meta.get("author", "")
            data["date"] = meta.get("date", "")
            data["description"] = meta.get("description", "")
            self.view_ctx["tmp"]["page_data"] = data
            self.view_ctx["tmp"]["page_meta"] = meta
            self.run_hook("get_page_data")
            file_data_list.append(self.view_ctx["tmp"]["page_data"])
        self.pop_item_in_dict(self.view_ctx["tmp"], "page_data", "page_meta")
        if sort_key not in ("title", "date"):
            sort_key = "title"
        return sorted(file_data_list, key=lambda x: u"{}_{}".format(x[sort_key], x["title"]), reverse=reverse)

    #theme
    @property
    def theme_name(self):
        return current_app.config.get("THEME_NAME")

    def theme_path_for(self, tmpl_name):
        return os.path.join(self.theme_name, "{}{}".format(tmpl_name, TEMPLATE_FILE_EXT))

    # context
    def init_context(self):
        # env context
        config = self.config
        self.view_ctx["config"] = config
        self.view_ctx["base_url"] = config.get("BASE_URL")
        self.view_ctx["theme_path_for"] = self.theme_path_for
        self.view_ctx["site_title"] = config.get("SITE_TITLE")
        self.view_ctx["site_author"] = config.get("SITE_AUTHOR")
        self.view_ctx["site_description"] = config.get("SITE_DESCRIPTION")
        return

    #hook
    def run_hook(self, hook_name, *cleanup_keys):
        for plugin_module in self.plugins:
            func = plugin_module.__dict__.get(hook_name)
            if callable(func):
                func(self.config, ImmutableDict(self.view_ctx), self.ext_ctx)
        self.cleanup_context(*cleanup_keys)
        return

    # cleanup
    @staticmethod
    def pop_item_in_dict(d, *keys):
        for key in keys:
            if key in d:
                d.pop(key)
        return

    def cleanup_context(self, *keys):
        self.pop_item_in_dict(self.view_ctx, *keys)
        return


class ContentView(BaseView):
    def get(self, _):
        # init
        status_code = 200
        is_not_found = False
        content_file_full_path = None
        run_hook = self.run_hook

        # load
        self.load_plugins()
        run_hook("plugins_loaded")

        load_config(current_app)
        self.init_context()
        run_hook("config_loaded")

        request_url = request.path
        site_index_url = current_app.config.get("SITE_INDEX_URL")
        is_site_index = request_url == site_index_url
        auto_index = is_site_index and current_app.config.get("AUTO_INDEX")
        self.view_ctx["request"] = request
        self.view_ctx["is_site_index"] = is_site_index
        self.view_ctx["auto_index"] = auto_index
        run_hook("request_url", "request")

        if not auto_index:
            content_file_full_path = self.get_file_path(request_url)
            # hook before load content
            self.view_ctx["file_path"] = content_file_full_path
            run_hook("before_load_content")
            # if not found
            if content_file_full_path is None:
                is_not_found = True
                status_code = 404
                content_file_full_path = self.view_ctx["not_found_file_path"] = self.content_not_found_full_path
                if not self.check_file_exists(content_file_full_path):
                    # without not found file
                    abort(404)

            # read file content
            if is_not_found:
                run_hook("before_404_load_content")
            with open(content_file_full_path, "r") as f:
                self.view_ctx["file_content"] = f.read().decode(CHARSET)
            if is_not_found:
                run_hook("after_404_load_content", "not_found_file_path")
            run_hook("after_load_content", "file_path")

            # parse file content
            meta_string, content_string = self.content_splitter(self.view_ctx["file_content"])

            self.view_ctx["meta"] = self.parse_file_meta(meta_string)
            run_hook("file_meta")

            self.view_ctx["content_string"] = content_string
            run_hook("before_parse_content", "content_string")
            self.view_ctx["content"] = self.parse_content(content_string)
            run_hook("after_parse_content")

        # content index
        pages = self.get_pages("date", True)
        self.view_ctx["pages"] = filter(lambda x: x["url"] != site_index_url, pages)
        self.view_ctx["current_page"] = defaultdict(str)
        self.view_ctx["prev_page"] = defaultdict(str)
        self.view_ctx["next_page"] = defaultdict(str)
        self.view_ctx["is_front_page"] = False
        self.view_ctx["is_tail_page"] = False
        for page_index, page_data in enumerate(self.view_ctx["pages"]):
            if auto_index:
                break
            if page_data["path"] == content_file_full_path:
                self.view_ctx["current_page"] = page_data
                if page_index == 0:
                    self.view_ctx["is_front_page"] = True
                else:
                    self.view_ctx["prev_page"] = self.view_ctx["pages"][page_index-1]
                if page_index == len(self.view_ctx["pages"]) - 1:
                    self.view_ctx["is_tail_page"] = True
                else:
                    self.view_ctx["next_page"] = self.view_ctx["pages"][page_index+1]
            page_data.pop("path")
        run_hook("get_pages")

        self.view_ctx["template_file_path"] = self.theme_path_for(DEFAULT_INDEX_TMPL_NAME) if auto_index \
            else self.theme_path_for(self.view_ctx["meta"].get("template", DEFAULT_POST_TMPL_NAME))

        run_hook("before_render")
        self.view_ctx.update(self.ext_ctx)
        self.view_ctx["output"] = render_template(self.view_ctx["template_file_path"], **self.view_ctx)
        run_hook("after_render", "template_file_path")

        if "output" in self.ext_ctx:
            self.view_ctx["output"] = self.ext_ctx["output"]
        return make_content_response(self.view_ctx["output"], status_code)


app = Flask(__name__, static_url_path=STATIC_BASE_URL)
load_config(app)
app.debug = app.config.get("DEBUG")
app.static_folder = STATIC_DIR
app.template_folder = THEME_DIR
app.add_url_rule("/favicon.ico", redirect_to="{}/favicon.ico".format(STATIC_BASE_URL), endpoint="favicon.ico")
app.add_url_rule("/", defaults={"_": ""}, view_func=ContentView.as_view("index"))
app.add_url_rule("/<path:_>", view_func=ContentView.as_view("content"))


@app.errorhandler(Exception)
def errorhandler(err):
    err_msg = "{}".format(repr(err))
    current_app.logger.error(err_msg)
    return make_response(err_msg, 579)


if __name__ == "__main__":
    host = app.config.get("HOST")
    port = app.config.get("PORT")
    app.run(host=host, port=port, use_reloader=False)