#coding=utf-8
from __future__ import absolute_import

PLUGIN_DIR = "plugins/"

THEME_DIR = "themes"
TEMPLATE_FILE_EXT = ".html"
DEFAULT_INDEX_TMPL_NAME = "index"
DEFAULT_POST_TMPL_NAME = "post"
DEFAULT_DATE_FORMAT = '%Y/%m/%d'

STATIC_DIR = THEME_DIR
STATIC_BASE_URL = '/themes'

CONTENT_DIR = "content/"
CONTENT_FILE_EXT = ".md"
CONTENT_DEFAULT_FILENAME = "index"
CONTENT_NOT_FOUND_FILENAME = "404"

CHARSET = "utf8"

import sys
sys.path.insert(0, PLUGIN_DIR)

from flask import Flask, current_app, request, abort, render_template, make_response, redirect
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

from datetime import datetime
import traceback

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
        base_files.extend(self.config.get("IGNORE_FILES"))
        return base_files

    @staticmethod
    def content_splitter(file_content):
        pattern = r"(\n)*/\*(\n)*(?P<meta>(.*\n)*)\*/(?P<content>(.*(\n)?)*)"
        re_pattern = re.compile(pattern)
        m = re_pattern.match(file_content)
        if m is None:
            return "", ""
        return m.group("meta"), m.group("content")

    def parse_post_meta(self, meta_string):
        headers = dict()
        self.run_hook("before_read_post_meta", headers = headers)

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

    # posts
    @staticmethod
    def get_files(base_dir, ext):
        all_files = []
        for root, directory, files in os.walk(base_dir):
            file_full_paths = [os.path.join(root, f) for f in filter(lambda x: x.endswith(ext), files)]
            all_files.extend(file_full_paths)
        return all_files

    def format_date(self, date):
        config = self.config
        date_format = DEFAULT_DATE_FORMAT
        try:
            date_object=datetime.strptime(date, date_format)
            date_formatted=date_object.strftime(config.get('POST_DATE_FORMAT'))
        except ValueError:
            date_formatted=date
        return date_formatted
        
    def get_posts(self):
        config = self.config
        base_url = config.get("BASE_URL")
        
        sort_key=config.get("POST_ORDER_BY")
        order=config.get("POST_ORDER")
        
        reverse = False
        if order == 'desc':
            reverse = True

        files = self.get_files(CONTENT_DIR, CONTENT_FILE_EXT)
        post_data_list = []
        for f in files:
            relative_path = f.split(CONTENT_DIR, 1)[1]
            if relative_path.startswith("~") \
                    or relative_path.startswith("#") \
                    or relative_path in self.content_ignore_files:
                continue
            with open(f, "r") as fh:
                file_content = fh.read().decode(CHARSET)
            meta_string, content_string = self.content_splitter(file_content)
            meta = self.parse_post_meta(meta_string)
            data = dict()
            # generate request url
            if relative_path.endswith(CONTENT_FILE_EXT):
                relative_path = relative_path[:-len(CONTENT_FILE_EXT)]

            if relative_path.endswith("index"):
                relative_path = relative_path[:-5]

            url = "{}/{}".format(base_url,relative_path)

            data["path"] = f
            data["title"] = meta.get("title", "")
            data["url"] = url
            data["author"] = meta.get("author", "")
            data["date"] = meta.get("date", "")
            data["date_formatted"] = self.format_date(meta.get("date", ""))
            data["description"] = meta.get("description", "")
            
            self.run_hook("get_post_data",data = data, post_meta = meta.copy())
            post_data_list.append(data)
        if sort_key not in ("title", "date"):
            sort_key = "title"
        return sorted(post_data_list, key=lambda x: u"{}_{}".format(x[sort_key], x["title"]), reverse=reverse)

    #theme
    @property
    def theme_name(self):
        return self.config.get("THEME_NAME")

    def theme_path_for(self, tmpl_name):
        return os.path.join(self.theme_name, "{}{}".format(tmpl_name, TEMPLATE_FILE_EXT))

    # context
    def init_context(self):
        # env context
        config = self.config
        theme_relative_path = os.path.join(THEME_DIR,config.get("THEME_NAME"))
        theme_url = os.path.join(config.get("BASE_URL"),theme_relative_path);
        self.view_ctx["config"] = config
        self.view_ctx["base_url"] = config.get("BASE_URL")
        self.view_ctx["theme_url"] = theme_url
        self.view_ctx["theme_path_for"] = self.theme_path_for
        self.view_ctx["site_title"] = config.get("SITE_TITLE")
        self.view_ctx["site_author"] = config.get("SITE_AUTHOR")
        self.view_ctx["site_description"] = config.get("SITE_DESCRIPTION")
        return

    #hook
    def run_hook(self, hook_name, **references):
        for plugin_module in self.plugins:
            func = plugin_module.__dict__.get(hook_name)
            if callable(func):
                func(**references)
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
        self.config = current_app.config
        
        self.init_context()
        
        run_hook("config_loaded", config = self.config)
        
        config = self.config
        
        request_url = request.path
        site_index_url = config.get("SITE_INDEX_URL")
        is_site_index = request_url == site_index_url
        auto_index = is_site_index and config.get("AUTO_INDEX")
        self.view_ctx["is_site_index"] = is_site_index
        self.view_ctx["auto_index"] = auto_index
        run_hook("request_url", request = request)

        if not auto_index:
            content_file_full_path = self.get_file_path(request_url)
            # hook before load content
            run_hook("before_load_content",file = content_file_full_path)
            # if not found
            if content_file_full_path is None:
                is_not_found = True
                status_code = 404
                content_file_full_path = self.content_not_found_full_path
                if not self.check_file_exists(content_file_full_path):
                    # without not found file
                    abort(404)

            # read file content
            if is_not_found:
                run_hook("before_404_load_content",file = content_file_full_path)
            with open(content_file_full_path, "r") as f:
                file_content = f.read().decode(CHARSET)
            if is_not_found:
                run_hook("after_404_load_content",file = content_file_full_path, content = file_content)
            run_hook("after_load_content", file = content_file_full_path,content = file_content)
            
            # parse file content
            meta_string, content_string = self.content_splitter(file_content)
            post_meta=self.parse_post_meta(meta_string)

            redirect_to = {"url":None}
            run_hook("single_post_meta", post_meta = post_meta, redirect_to = redirect_to)
            if redirect_to.get("url"):
                return redirect(redirect_to["url"], code=302)
            self.view_ctx["meta"] = post_meta

            run_hook("before_parse_content", content = content_string)
            post_content = self.parse_content(content_string)
            run_hook("after_parse_content", content = post_content)
            self.view_ctx["content"] = post_content
        # content index
        posts = self.get_posts()
        self.view_ctx["posts"] = filter(lambda x: x["url"] != site_index_url, posts)
        self.view_ctx["current_post"] = defaultdict(str)
        self.view_ctx["prev_post"] = defaultdict(str)
        self.view_ctx["next_post"] = defaultdict(str)
        self.view_ctx["is_front"] = False
        self.view_ctx["is_tail"] = False
        for post_index, post_data in enumerate(self.view_ctx["posts"]):
            if auto_index:
                break
            if post_data["path"] == content_file_full_path:
                self.view_ctx["current_post"] = post_data
                if post_index == 0:
                    self.view_ctx["is_front"] = True
                else:
                    self.view_ctx["prev_post"] = self.view_ctx["posts"][post_index-1]
                if post_index == len(self.view_ctx["posts"]) - 1:
                    self.view_ctx["is_tail"] = True
                else:
                    self.view_ctx["next_post"] = self.view_ctx["posts"][post_index+1]
            post_data.pop("path")

        run_hook("get_posts",posts = self.view_ctx["posts"], current_post = self.view_ctx["current_post"],
            prev_post = self.view_ctx["prev_post"],next_post = self.view_ctx["next_post"])
        
        template = DEFAULT_INDEX_TMPL_NAME if auto_index else self.view_ctx["meta"].get("template", DEFAULT_POST_TMPL_NAME)
        self.view_ctx["template_file_path"] = self.theme_path_for(template)
        
        run_hook("before_render",var = self.view_ctx, template = template)
        self.view_ctx["template"] = template
        
        output = render_template(self.view_ctx["template_file_path"], **self.view_ctx)
        
        run_hook("after_render", output = output)
        return make_content_response(output, status_code)

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
    err_msg = "{}\n{}".format(repr(err),traceback.format_exc())
    current_app.logger.error(err_msg)
    return make_response(repr(err), 579)


if __name__ == "__main__":
    host = app.config.get("HOST")
    port = app.config.get("PORT")
    app.run(host=host, port=port)