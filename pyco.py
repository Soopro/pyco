#coding=utf-8
from __future__ import absolute_import

PLUGIN_DIR = "plugins/"

THEMES_DIR = "themes/"
TEMPLATE_FILE_EXT = ".html"
TPL_FILE_EXT = ".tpl"
DEFAULT_INDEX_TMPL_NAME = "index"
DEFAULT_PAGE_TMPL_NAME = "page"
DEFAULT_DATE_FORMAT = '%Y/%m/%d'

DEFAULT_EXCERPT_LENGTH = 50
DEFAULT_EXCERPT_ELLIPSIS = "&hellip"

STATIC_DIR = THEMES_DIR
STATIC_BASE_URL = "/static"

UPLOADS_DIR = "uploads/"
UPLOADS_URL = "/uploads"

EDITOR_DIR = "editor/"
EDITOR_URL = "/editor"
EDITOR_INDEX = "editor/index.html"

CONTENT_DIR = "content/"
CONTENT_FILE_EXT = ".md"
CONTENT_DEFAULT_FILENAME = "index"
CONTENT_NOT_FOUND_FILENAME = "404"

INVISIBLE_PAGE_LIST = [CONTENT_NOT_FOUND_FILENAME]

CHARSET = "utf8"

import sys
sys.path.insert(0, PLUGIN_DIR)

from flask import Flask, current_app, request, abort, render_template, make_response, redirect, send_from_directory, send_file
from flask.views import MethodView
from jinja2 import FileSystemLoader
from helpers import load_config, make_content_response
from collections import defaultdict
from hashlib import sha1
from werkzeug.datastructures import ImmutableDict
from types import ModuleType
from datetime import datetime
from optparse import OptionParser
import os, re, traceback, markdown
# import misaka
# from pygments import highlight
# from pygments.lexers import get_lexer_by_name
# from pygments.formatters.html import HtmlFormatter

# class BleepRenderer(misaka.HtmlRenderer, misaka.SmartyPants):
#     @staticmethod
#     def block_code(text, lang):
#         if not lang:
#             return '\n<pre><code>%s</code></pre>\n' % text.strip()
#         lexer = get_lexer_by_name(lang, stripall=True)
#         formatter = HtmlFormatter(style="vim", title="%s code" % lang, cssclass="codehilite")
#         return highlight(text, lexer, formatter)


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
                except ImportError as err:
                    raise
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

    def parse_page_meta(self, meta_string):
        headers = dict()
        self.run_hook("before_read_page_meta", headers = headers)

        for line in meta_string.split("\n"):
            kv_pair = line.split(":", 1)
            if len(kv_pair) == 2:
                headers[kv_pair[0].lower()] = kv_pair[1].strip()
        self.run_hook("after_read_page_meta", headers = headers)
        return headers

    @staticmethod
    def parse_content(content_string):
        # extensions = misaka.EXT_NO_INTRA_EMPHASIS | misaka.EXT_FENCED_CODE | misaka.EXT_AUTOLINK | \
#             misaka.EXT_LAX_HTML_BLOCKS | misaka.EXT_TABLES | misaka.EXT_SUPERSCRIPT
#         flags = misaka.HTML_TOC | misaka.HTML_USE_XHTML
#         render = BleepRenderer(flags=flags)
#         md = misaka.Markdown(render, extensions=extensions)
        return markdown.markdown(content_string,['markdown.extensions.codehilite','markdown.extensions.extra'])

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

    def format_date(self, date):
        config = self.config
        date_format = DEFAULT_DATE_FORMAT
        try:
            date_object=datetime.strptime(date, date_format)
            date_formatted=date_object.strftime(config.get('PAGE_DATE_FORMAT'))
        except ValueError:
            date_formatted=date
        return date_formatted
        
    def get_pages(self):
        config = self.config
        base_url = helper_gen_base_url()
        
        sort_key=config.get("PAGE_ORDER_BY")
        order=config.get("PAGE_ORDER")
        
        reverse = False
        if order == 'desc':
            reverse = True

        files = self.get_files(CONTENT_DIR, CONTENT_FILE_EXT)
        page_data_list = []
        for f in files:
            if f in INVISIBLE_PAGE_LIST:
                continue
            relative_path = f.split(CONTENT_DIR, 1)[1]
            if relative_path.startswith("~") \
                    or relative_path.startswith("#") \
                    or relative_path in self.content_ignore_files:
                continue
            with open(f, "r") as fh:
                file_content = fh.read().decode(CHARSET)
            meta_string, content_string = self.content_splitter(file_content)
            meta = self.parse_page_meta(meta_string)
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
            data["updated"] = meta.get("updated", "")
            data["date"] = meta.get("date", "")
            data["date_formatted"] = self.format_date(meta.get("date", ""))
            data["content"] = self.parse_content(content_string)
            data["excerpt"] = helper_gen_excerpt(data["content"],self.view_ctx["theme_meta"])
            des = meta.get("description")
            data["description"] = data["excerpt"] if not des else des
            self.run_hook("get_page_data",data = data, page_meta = meta.copy())
            page_data_list.append(data)
        if sort_key not in ("title", "date"):
            sort_key = "title"
        return sorted(page_data_list, key=lambda x: u"{}_{}".format(x[sort_key], x["title"]), reverse=reverse)

    #theme
    @property
    def theme_name(self):
        return self.config.get("THEME_NAME")

    def theme_path_for(self, tmpl_name):
        return "{}{}".format(tmpl_name, TEMPLATE_FILE_EXT)
        # return os.path.join(self.theme_name, "{}{}".format(tmpl_name, TEMPLATE_FILE_EXT))

    # context
    def init_context(self):
        # env context
        config = self.config
        self.view_ctx["base_url"] = helper_gen_base_url()
        self.view_ctx["theme_url"] = helper_gen_theme_url()
        self.view_ctx["site_meta"] = config.get("SITE_META")
        self.view_ctx["theme_meta"] = config.get("THEME_META")
        return
    
    #hook
    def run_hook(self, hook_name, **references):
        for plugin_module in self.plugins:
            func = plugin_module.__dict__.get(hook_name)
            if callable(func):
                func(**references)
        return


class ContentView(BaseView):
    def get(self, _):
        # init
        status_code = 200
        is_not_found = False
        run_hook = self.run_hook
        
        #for pass intor hook
        file = {"path": None}
        file_content = {"content": None}
        
        # load
        self.load_plugins()
        run_hook("plugins_loaded")

        # load_config(current_app)
        current_app.debug = _DEBUG
        self.config = current_app.config
        
        self.init_context()
        
        run_hook("config_loaded", config = self.config)
        
        config = self.config
        
        request_url = request.path
        site_index_url = config.get("SITE_INDEX_URL")
        is_site_index = request_url == site_index_url
        auto_index = is_site_index and config.get("AUTO_INDEX")
        self.view_ctx["is_site_index"] = is_site_index
        # self.view_ctx["auto_index"] = auto_index
        self.view_ctx["args"] = {k:v for k,v in request.args.iteritems()}
        
        redirect_to = {"url":None}
        run_hook("request_url", request = request, redirect_to = redirect_to)
        if redirect_to.get("url"):
            return redirect(redirect_to["url"], code=302)


        file["path"] = self.get_file_path(request_url)
        # hook before load content
        run_hook("before_load_content",file = file)
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
            run_hook("before_404_load_content",file = file)

        with open(file['path'], "r") as f:
            file_content['content'] = f.read().decode(CHARSET)
        
        
        if is_not_found:
            run_hook("after_404_load_content",file = file, content = file_content)
        run_hook("after_load_content", file = file, content = file_content)
        
        # parse file content
        meta_string, content_string = self.content_splitter(file_content["content"])
        page_meta=self.parse_page_meta(meta_string)
        page_meta['date_formatted'] = self.format_date(page_meta.get("date", ""))
        redirect_to = {"url":None}
        run_hook("single_page_meta", page_meta = page_meta, redirect_to = redirect_to)
        
        tmp_tpl_name=str(page_meta.get('template'))
        if tmp_tpl_name[0:1]=='_' and not redirect_to["url"]:
            redirect_to["url"] = os.path.join(config.get('BASE_URL'),CONTENT_NOT_FOUND_FILENAME)
        
        if redirect_to.get("url"):
            return redirect(redirect_to["url"], code=302)

        self.view_ctx["meta"] = page_meta
        
        page_content = {}
        
        page_content['content'] = content_string
        run_hook("before_parse_content", content = page_content)
        
        page_content['content'] = self.parse_content(page_content['content'])
        run_hook("after_parse_content", content = page_content)
        
        self.view_ctx["content"] = page_content['content']
        

        excerpt = helper_gen_excerpt(self.view_ctx["content"],self.view_ctx["theme_meta"])
        self.view_ctx["meta"]["excerpt"] = excerpt
        des = self.view_ctx["meta"].get("description")
        self.view_ctx["meta"]["description"] = excerpt if not des else des
            
        # content index
        pages = self.get_pages()
        # self.view_ctx["pages"] = filter(lambda x: x["url"] != site_index_url, pages)
        self.view_ctx["pages"] = pages
        self.view_ctx["current_page"] = defaultdict(str)
        self.view_ctx["prev_page"] = defaultdict(str)
        self.view_ctx["next_page"] = defaultdict(str)
        self.view_ctx["is_front"] = False
        self.view_ctx["is_tail"] = False
        for page_index, page_data in enumerate(self.view_ctx["pages"]):
            if auto_index:
                break
            if page_data["path"] == file['path']:
                self.view_ctx["current_page"] = page_data
                if page_index == 0:
                    self.view_ctx["is_front"] = True
                else:
                    self.view_ctx["prev_page"] = self.view_ctx["pages"][page_index-1]
                if page_index == len(self.view_ctx["pages"]) - 1:
                    self.view_ctx["is_tail"] = True
                else:
                    self.view_ctx["next_page"] = self.view_ctx["pages"][page_index+1]
            page_data.pop("path")

        run_hook("get_pages",pages = self.view_ctx["pages"], current_page = self.view_ctx["current_page"],
            prev_page = self.view_ctx["prev_page"], next_page = self.view_ctx["next_page"])
        
        template = {}
        template['file'] = DEFAULT_INDEX_TMPL_NAME if auto_index else self.view_ctx["meta"].get("template", DEFAULT_PAGE_TMPL_NAME)
        
        run_hook("before_render",var = self.view_ctx, template = template)
        
        template_file_path = self.theme_path_for(template['file'])
        template_file_absolute_path = os.path.join(current_app.root_path, current_app.template_folder, template_file_path)

        if not os.path.isfile(template_file_absolute_path):
            template['file'] = None
            template_file_path = self.theme_path_for(DEFAULT_PAGE_TMPL_NAME)

        self.view_ctx["template"] = template['file']
        self.view_ctx["template_file_path"] = template_file_path
        
        output = {}
        self.view_ctx.get('meta')
        output['content'] = render_template(self.view_ctx["template_file_path"], **self.view_ctx)
        
        run_hook("after_render", output = output)
        return make_content_response(output['content'], status_code)


class UploadView(MethodView):
    def get(self, filename):
        return send_from_directory(UPLOADS_DIR, filename)
        
class EditorView(MethodView):
    def get(self, filename=None):
        if not filename:
            return send_file(EDITOR_INDEX)
        return send_from_directory(EDITOR_DIR, filename)


class EditTemplateView(BaseView):
    def get(self, filename=None):
        if filename:
            file = ''.join([filename, TPL_FILE_EXT])

            # load_config(current_app)
            f = os.path.join(current_app.root_path, THEMES_DIR, current_app.config['THEME_NAME'], file)

            theme_url = helper_gen_theme_url()
            base_url = helper_gen_base_url()
            locale = current_app.config.get("SITE_META",{}).get('locale')
            tmpl_content = helper_parse_template(f)
            # make fake template context
            shortcodes  = [
                {"pattern":u"base_url","replacement":base_url},
                {"pattern":u"theme_url","replacement":theme_url},
                {"pattern":u"locale","replacement":locale}
            ]
            for code in shortcodes:
                pattern = helper_make_pattern(code["pattern"])
                tmpl_content = re.sub(pattern, code["replacement"], tmpl_content)
            
            return tmpl_content

def helper_gen_base_url():
    return os.path.join(current_app.config.get("BASE_URL"),'')

def helper_gen_theme_url():
    return os.path.join(STATIC_BASE_URL,current_app.config.get('THEME_NAME'),'')


def helper_gen_excerpt(content,theme_meta):
    excerpt_length = theme_meta.get('excerpt_length', DEFAULT_EXCERPT_LENGTH)
    excerpt_ellipsis = theme_meta.get('excerpt_ellipsis', DEFAULT_EXCERPT_ELLIPSIS)
    excerpt = re.sub(r'<[^>]*?>', '', content)
    if excerpt:
        excerpt = " ".join(excerpt.split())
        excerpt = excerpt[0:excerpt_length]+excerpt_ellipsis
    return excerpt

def helper_parse_template(path):
    with open(path, "r") as f:
        content = f.read()
        content = content.decode("utf8")
        return content

def helper_make_pattern(pattern):
    return re.compile(r"{}\s*{}\s*{}".format('{{',pattern,'}}'), re.IGNORECASE)


app = Flask(__name__, static_url_path=STATIC_BASE_URL)
load_config(app)


opt = OptionParser()
opt.add_option('-s','--server', help='set server mode',
                action='store_const', dest='server', const=True, default=False)
opt.add_option('-d','--debug', help='set debug mode',
                action='store_const', dest='debug', const=True, default=False)
opts, args = opt.parse_args()

_DEBUG = app.config.get("DEBUG")
if opts.server:
    _DEBUG = False
elif opts.debug:
    _DEBUG = True

app.debug = _DEBUG
app.jinja_env.autoescape = False
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.jinja_env.add_extension('jinja2.ext.i18n')
app.jinja_env.add_extension('jinja2.ext.do')
app.jinja_env.add_extension('jinja2.ext.with_')
app.template_folder = os.path.join(THEMES_DIR,app.config.get("THEME_NAME"))
app.static_folder = THEMES_DIR
# app.add_url_rule("/favicon.ico", redirect_to="{}/favicon.ico".format(STATIC_BASE_URL), endpoint="favicon.ico")
app.add_url_rule("/", defaults={"_": ""}, view_func=ContentView.as_view("index"))
app.add_url_rule("{}/".format(EDITOR_URL), view_func=EditorView.as_view("editor"))
app.add_url_rule("/<path:_>", view_func=ContentView.as_view("content"))
app.add_url_rule("{}/<path:filename>".format(UPLOADS_URL), view_func=UploadView.as_view("uploads"))
app.add_url_rule("{}/<path:filename>".format(EDITOR_URL), view_func=EditorView.as_view("editor_static"))
app.add_url_rule("{}/tpl/<path:filename>".format(EDITOR_URL), view_func=EditTemplateView.as_view("tpl_file"))


@app.before_request
def before_request():
    load_config(current_app)
    if current_app.debug:
        current_app.logger.debug("Pyco is running in DEBUG mode !!! Jinja2 template folder is about to reload.")
        # change template folder
        current_app.template_folder = os.path.join(THEMES_DIR,current_app.config.get("THEME_NAME"))
        # change reload template folder
        current_app.jinja_env.cache = None
        current_app.jinja_loader = FileSystemLoader(current_app.template_folder)
        # current_app._get_current_object().jinja_loader = FileSystemLoader(current_app.template_folder)


@app.errorhandler(Exception)
def errorhandler(err):
    err_msg = "{}\n{}".format(repr(err),traceback.format_exc())
    current_app.logger.error(err_msg)
    return make_response(repr(err), 579)


if __name__ == "__main__":
    host = app.config.get("HOST")
    port = app.config.get("PORT")
    app.run(host=host, port=port)