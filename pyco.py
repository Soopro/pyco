#coding=utf-8
from __future__ import absolute_import

from flask import (Flask, current_app, request, abort, render_template, g,
                   make_response, redirect, send_from_directory, send_file)

from flask.views import MethodView
from jinja2 import FileSystemLoader

from helpers import load_config, make_content_response, helper_process_url

from collections import defaultdict
from hashlib import sha1
from werkzeug.datastructures import ImmutableDict
from types import ModuleType
from datetime import datetime
from gettext import gettext, ngettext
import sys, os, re, traceback, markdown, json, argparse, yaml


class BaseView(MethodView):
    def __init__(self):
        super(BaseView, self).__init__()
        self.plugins = []
        self.config = current_app.config
        self.view_ctx = dict()
        # os.chdir(BASE_DIR)
        # live reload will fail if chdir.
        return
    
    def load_metas(self):
        theme_meta_file = os.path.join(THEMES_DIR,
                                       self.config['THEME_NAME'],
                                       DEFAULT_THEME_META_FILE)
        theme_meta = open(theme_meta_file)
        try:
            self.config['THEME_META'] = json.load(theme_meta)
        except Exception as e:
            err_msg = "Load Theme Meta faild: {}".format(str(e))
            raise Exception(err_msg)
        theme_meta.close()
        
        site_meta_file = os.path.join(CONTENT_DIR, DEFAULT_SITE_META_FILE)
        site_meta = open(site_meta_file)
        try:
            self.config['SITE'] = json.load(site_meta)
        except Exception as e:
            err_msg = "Load Site Meta faild: {}".format(str(e))
            raise Exception(err_msg)
        site_meta.close()
        
    
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

        tmp_fname = "{}{}".format(DEFAULT_INDEX_ALIAS, CONTENT_FILE_EXT)
        file_name = os.path.join(base_path, tmp_fname)
        if self.check_file_exists(file_name):
            return file_name
        return None
    
    def gen_base_url(self):
        return os.path.join(current_app.config.get("BASE_URL"))

    def gen_theme_url(self):
        return os.path.join(STATIC_BASE_URL,
                            current_app.config.get('THEME_NAME'))

    def gen_page_url(self, relative_path):
        if relative_path.endswith(CONTENT_FILE_EXT):
            relative_path = os.path.splitext(relative_path)[0]
        front_page_content_path = "{}/{}".format(CONTENT_DIR,
                                                 DEFAULT_INDEX_ALIAS)
        if relative_path.endswith(front_page_content_path):
            len_index_str = len(DEFAULT_INDEX_ALIAS)
            relative_path = relative_path[:-len_index_str]

        relative_url = relative_path.replace(CONTENT_DIR+"/", '')
        url = os.path.join(current_app.config.get("BASE_URL"), relative_url)
        return url
    
    def gen_page_alias(self, relative_path):
        if relative_path.endswith(CONTENT_FILE_EXT):
            relative_path = os.path.splitext(relative_path)[0]
        alias = relative_path.split('/')[-1]
        return alias

    def gen_excerpt(self, content, theme_meta):
        excerpt_length = theme_meta.get('excerpt_length',
                                        DEFAULT_EXCERPT_LENGTH)
                                        
        excerpt_ellipsis = theme_meta.get('excerpt_ellipsis',
                                          DEFAULT_EXCERPT_ELLIPSIS)
                                          
        excerpt = re.sub(r'<[^>]*?>', '', content)
        if excerpt:
            excerpt = " ".join(excerpt.split())
            excerpt = excerpt[0:excerpt_length]+excerpt_ellipsis
        return excerpt

    @staticmethod
    def check_file_exists(file_full_path):
        return os.path.isfile(file_full_path)

    # content
    @property
    def content_not_found_relative_path(self):
        return "{}{}".format(DEFAULT_404_ALIAS, CONTENT_FILE_EXT)

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
        self.run_hook("before_read_page_meta", headers=headers)
        
        def convert_data(x):
            if isinstance(x, dict):
                return dict((k.lower(), convert_data(v)) 
                             for k, v in x.iteritems())
            elif isinstance(x, list):
                return list([convert_data(i) for i in x])
            elif isinstance(x, str):
                return x.decode("utf-8")
            elif isinstance(x, (unicode, int, float, bool)):
                return x
            else:
                try:
                    x = str(x).decode("utf-8")
                except Exception as e:
                    print e
                    pass
            return x
        
        yaml_data = yaml.safe_load(meta_string)
        headers = convert_data(yaml_data)
#         for line in meta_string.split("\n"):
#             kv_pair = line.split(":", 1)
#             if len(kv_pair) == 2:
#                 _tmp_value = kv_pair[1].strip()
#                 try:
#                     _tmp_value = ast.literal_eval(_tmp_value)
#                     _tmp_value = convert_unicode(_tmp_value)
#                 except Exception:
#                     pass
#
#                 headers[kv_pair[0].lower()] = _tmp_value

        self.run_hook("after_read_page_meta", headers=headers)
        return headers

    @staticmethod
    def parse_content(content_string, is_markdown=True):
        if is_markdown:
            return markdown.markdown(content_string,
                                     ['markdown.extensions.codehilite',
                                     'markdown.extensions.extra'])
        else:
            return content_string

    # cache
    @staticmethod
    def generate_etag(content_file_full_path):
        file_stat = os.stat(content_file_full_path)
        base = "{mtime:0.0f}_{size:d}_{fpath}".format(
                    mtime=file_stat.st_mtime,
                    size=file_stat.st_size,
                    fpath=content_file_full_path
                )
                    
        return sha1(base).hexdigest()

    # pages
    @staticmethod
    def get_files(base_dir, ext):
        all_files = []
        for root, directory, files in os.walk(base_dir):
            file_full_paths = [
                os.path.join(root, f) 
                for f in filter(lambda x: x.endswith(ext), files)
            ]
            all_files.extend(file_full_paths)
        return all_files

    def format_date(self, date):
        config = self.config
        date_format = DEFAULT_DATE_FORMAT
        theme_meta_options = self.view_ctx["theme_meta"].get("options")
        to_format = theme_meta_options.get('date_format')
        try:
            date_object = datetime.strptime(date, date_format)
            _fmted = date_object.strftime(to_format.encode('utf-8'))
            date_formatted = _fmted.decode('utf-8')
        except Exception as e:
            date_formatted = date
        return date_formatted
    
    def get_menus(self):
        menus = self.config['SITE'].get("menus",{})
        base_url = current_app.config.get("BASE_URL")
        def process_menu_url(menu):
            for item in menu:
                url = item.get("url")
                if isinstance(url, (str, unicode)) \
                and not re.match("^(?:http|ftp)s?://", url):
                    item["url"] = os.path.join(base_url, url.strip('/'))
                item["nodes"] = process_menu_url(item.get("nodes",[]))
            return menu
        for menu in menus:
            menus[menu] = process_menu_url(menus[menu])
        return menus
    
    def get_taxonomies(self):
        taxonomies = self.config['THEME_META'].get("taxonomies",[])
        terms = self.config['SITE'].get("terms",{})
        tax_dict = {}
        for tax in taxonomies:
            
            current_terms = terms.get(tax.get("alias"),[])
            
            tax_dict[tax["alias"]] = {
                "title": tax.get("title"),
                "alias": tax.get("alias"),
                "content_types": tax.get("content_types"),
                "terms": [
                    {
                        "alias": x.get("alias"),
                        "title": x.get("title"),
                        "locked": x.get("locked"),
                        "priority": x.get("priority"),
                        "meta": x.get("meta",{}),
                        "taxonomy": tax.get("alias"),
                        "updated": x.get("updated")
                    }
                    for x in current_terms
                ]
            }
            # del terms[tax["alias"]]
        
        return tax_dict
        
        
    def get_pages(self):
        config = self.config
        
        theme_meta_options = self.view_ctx["theme_meta"].get("options")
        
        # sortby
        sort_desc = True
        params_sortby = theme_meta_options.get("sortby", "updated")
        if params_sortby[0:1] == '-':
            sort_desc = False
            params_sortby = params_sortby[1:]
        elif params_sortby[0:1] == '+':
            params_sortby = params_sortby[1:]
    
        sort_key = params_sortby

        files = self.get_files(CONTENT_DIR, CONTENT_FILE_EXT)
        page_data_list = []
        for f in files:
            if f in INVISIBLE_PAGE_LIST:
                continue

            relative_path = f.split(CONTENT_DIR+"/", 1)[1]
            if relative_path.startswith("~") \
                or relative_path.startswith("#") \
                or relative_path in self.content_ignore_files:
                continue
            
            with open(f, "r") as fh:
                file_content = fh.read().decode(CHARSET)
            meta_string, content_string = self.content_splitter(file_content)
            meta = self.parse_page_meta(meta_string)
            data = self.parse_file_attrs(meta, f, content_string, False)
            self.run_hook("get_page_data", data=data, page_meta=meta.copy())
            page_data_list.append(data)
      
        
        return sorted(page_data_list, 
                      key=lambda x: (x['priority'], x[sort_key]),
                      reverse=sort_desc)

    #theme
    @property
    def theme_name(self):
        return self.config.get("THEME_NAME")

    def theme_path_for(self, tmpl_name):
        return "{}{}".format(tmpl_name, TEMPLATE_FILE_EXT)
        # return os.path.join(self.theme_name, "{}{}".format(tmpl_name, TEMPLATE_FILE_EXT))
    
    def theme_absolute_path_for(self, tmpl_path):
        return os.path.join(current_app.root_path,
                            current_app.template_folder,
                            tmpl_path)
    
    # attrs
    def parse_file_attrs(self, meta, file_path, content_string,
                         escape_content=True):
        data = dict()
        for m in meta:
            data[m] = meta[m]
        data["alias"] = self.gen_page_alias(file_path)
        if data["alias"] == DEFAULT_INDEX_ALIAS:
            data["is_front"] = True
        if data["alias"] == DEFAULT_404_ALIAS:
            data["is_404"] = True
        data["url"] = self.gen_page_url(file_path)
        data["title"] = meta.get("title", u"")
        data["priority"] = meta.get("priority", 0)
        data["author"] = meta.get("author", u"")
        # data['status'] = meta.get('status') # define by plugin
        # data['type'] = meta.get('type') # define by plugin
        data["updated"] = meta.get("updated", 0)
        data["date"] = meta.get("date", u"")
        data["date_formatted"] = self.format_date(meta.get("date", u""))
        content = self.parse_content(content_string)
        data["excerpt"] = self.gen_excerpt(content,
                                           self.view_ctx["theme_meta"])
        des = meta.get("description")
        data["description"] = data["excerpt"] if not des else des
        
        if not escape_content:
            data["content"] = content
        return data
    
    # context
    def init_context(self):
        # env context
        config = self.config
        self.view_ctx["app_id"] = "APP_ID_PLACE_HOLDER"
        self.view_ctx["base_url"] = self.gen_base_url()
        self.view_ctx["theme_url"] = self.gen_theme_url()
        self.view_ctx["site_meta"] = config.get("SITE",{}).get("meta")
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
        self.config = current_app.config
        self.load_metas()
        self.load_plugins()
        run_hook("plugins_loaded")

        current_app.debug = _DEBUG

        self.init_context()
        
        run_hook("config_loaded", config=self.config)
        
        config = self.config

        self.view_ctx["args"] = {k: v for k, v in request.args.iteritems()}
        
        redirect_to = {"url": None}
        run_hook("request_url", request=request, redirect_to=redirect_to)
        site_redirect_url = helper_process_url(redirect_to.get("url"),
                                               self.config.get("BASE_URL"))
        if site_redirect_url and request.url != site_redirect_url:
            return redirect(site_redirect_url, code=301)


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
        
        tmp_tpl_name = str(page_meta.get('template'))
        if tmp_tpl_name[0:1] == '_' and not redirect_to["url"]:
            redirect_to["url"] = os.path.join(config.get('BASE_URL'),
                                              DEFAULT_404_ALIAS)

        content_redirect_to = helper_process_url(redirect_to.get("url"),
                                                 self.config.get("BASE_URL"))
        if content_redirect_to and request.url != content_redirect_to:
            return redirect(redirect_to["url"], code=302)

        self.view_ctx["meta"] = page_meta
        
        page_content = dict()

        page_content['content'] = content_string
        run_hook("before_parse_content", content=page_content)
        
        page_content['content'] = self.parse_content(page_content['content'],
                                                     page_meta.get("markdown"))
        run_hook("after_parse_content", content=page_content)
        
        self.view_ctx["content"] = page_content['content']

        # excerpt = self.gen_excerpt(self.view_ctx["content"],
        #                            self.view_ctx["theme_meta"])
        # self.view_ctx["meta"]["excerpt"] = excerpt
        # des = self.view_ctx["meta"].get("description")
        # self.view_ctx["meta"]["description"] = excerpt if not des else des
        
        # menu
        self.view_ctx["menu"] = self.get_menus()
        
        # taxonomy
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

        template_file_path = self.theme_path_for(template['file'])
        template_file_absolute_path = self.theme_absolute_path_for(
                                                        template_file_path)
            
        if not os.path.isfile(template_file_absolute_path):
            template['file'] = None
            template_file_path = self.theme_path_for(DEFAULT_TEMPLATE)

        self.view_ctx["template"] = template['file']
        self.view_ctx["sa"] = {}
        
        output = {}
        self.view_ctx.get('meta')

        output['content'] = render_template(template_file_path,
                                            **self.view_ctx)
        run_hook("after_render", output=output)
        return make_content_response(output['content'], status_code)


class UploadView(MethodView):
    def get(self, filename):
        return send_from_directory(UPLOADS_DIR, filename)


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

EDITOR_DIR = app.config.get("EDITOR_DIR")
EDITOR_INDEX = app.config.get("EDITOR_INDEX")

CONTENT_DIR = app.config.get("CONTENT_DIR")
CONTENT_FILE_EXT = app.config.get("CONTENT_FILE_EXT")

DEFAULT_INDEX_ALIAS = app.config.get("DEFAULT_INDEX_ALIAS")
DEFAULT_404_ALIAS = app.config.get("DEFAULT_404_ALIAS")

INVISIBLE_PAGE_LIST = app.config.get("INVISIBLE_PAGE_LIST")

CHARSET = app.config.get("CHARSET")

# make importable for plugin folder
sys.path.insert(0, os.path.join(BASE_DIR, PLUGIN_DIR))

_DEBUG = app.config.get("DEBUG")

# options for start app
parser = argparse.ArgumentParser(
                description='Options of starting Pyco server.')

parser.add_argument('-s', '--production', 
                    dest='server_mode',
                    action='store_const',
                    const="PRD",
                    help='Manually start with production mode.')

parser.add_argument('-d', '--debug', 
                    dest='server_mode',
                    action='store_const',
                    const="DEBUG",
                    help='Manually start debug mode.')

args, unknown = parser.parse_known_args()

if args.server_mode is "DEBUG":
    _DEBUG = True
elif args.server_mode is "PRD":
    _DEBUG = False

# init app
app.debug = _DEBUG

# default multi language support
app.jinja_env.autoescape = False
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.jinja_env.add_extension('jinja2.ext.i18n')
app.jinja_env.add_extension('jinja2.ext.do')
app.jinja_env.add_extension('jinja2.ext.with_')
app.jinja_env.install_gettext_callables(gettext, ngettext, newstyle=True)
app.template_folder = os.path.join(THEMES_DIR, app.config.get("THEME_NAME"))
app.static_folder = THEMES_DIR
app.static_url_path = STATIC_BASE_URL

# routes
app.add_url_rule(
    STATIC_BASE_URL + '/<path:filename>',
    endpoint='static', view_func=app.send_static_file)

app.add_url_rule("/", defaults={"_": ""},
    view_func=ContentView.as_view("index"))

app.add_url_rule("/<path:_>", 
    view_func=ContentView.as_view("content"))
    
app.add_url_rule("/{}/<path:filename>".format(UPLOADS_DIR),
    view_func=UploadView.as_view("uploads"))


@app.before_first_request
def before_first_request():
    if current_app.debug:
        current_app.logger.debug(
            "Pyco is running in DEBUG mode !!! " +
            "Jinja2 template folder is about to reload.")


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
    return make_response(str(err), 579)


if __name__ == "__main__":
    host = app.config.get("HOST")
    port = app.config.get("PORT")
    app.run(host=host, port=port, debug=True)