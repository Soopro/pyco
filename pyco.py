#coding=utf-8
from __future__ import absolute_import

from flask import (Flask, current_app, request, abort, render_template, g,
                   make_response, redirect, send_from_directory, send_file)

from flask.views import MethodView
from jinja2 import FileSystemLoader

from helpers import (load_config, make_content_response, url_validator,
                     helper_make_dotted_dict, helper_process_url, sortby)

from collections import defaultdict
from hashlib import sha1
from werkzeug.datastructures import ImmutableDict
from types import ModuleType
from datetime import datetime
from gettext import gettext, ngettext
import sys, os, re, traceback, markdown, json, argparse, mimetypes, yaml

__version_info__ = ('1', '8', '0')
__version__ = '.'.join(__version_info__)


class BaseView(MethodView):
    def __init__(self):
        super(BaseView, self).__init__()
        self.plugins = []
        self.config = current_app.config
        self.type = None
        self.max_mode = True
        self.view_ctx = dict()
        # os.chdir(BASE_DIR)
        # live reload will fail if chdir.
        return
    
    def load_metas(self):
        config = self.config
        theme_meta_file = os.path.join(config.get('THEMES_DIR'),
                                       config.get('THEME_NAME'),
                                       config.get('DEFAULT_THEME_META_FILE'))
        theme_meta = open(theme_meta_file)
        try:
            self.config['THEME_META'] = json.load(theme_meta)
        except Exception as e:
            err_msg = "Load Theme Meta faild: {}".format(str(e))
            raise Exception(err_msg)
        theme_meta.close()
        
        site_meta_file = os.path.join(config.get('CONTENT_DIR'),
                                      config.get('DEFAULT_SITE_META_FILE'))

        site_meta = open(site_meta_file)
        try:
            self.config['SITE'] = json.load(site_meta)
        except Exception as e:
            err_msg = "Load Site Meta faild: {}".format(str(e))
            raise Exception(err_msg)
        site_meta.close()
        
    
    def load_plugins(self, plugins):
        loaded_plugins = []
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
        content_dir = self.config.get('CONTENT_DIR')
        content_ext = self.config.get('CONTENT_FILE_EXT')
        default_index_alias = self.config.get("DEFAULT_INDEX_ALIAS")
        
        base_path = os.path.join(content_dir, url[1:]).rstrip("/")
        file_name = "{}{}".format(base_path, content_ext)
        if self.check_file_exists(file_name):
            return file_name

        tmp_fname = "{}{}".format(default_index_alias, content_ext)
        file_name = os.path.join(base_path, tmp_fname)
        if self.check_file_exists(file_name):
            return file_name
        return None
    
    def gen_base_url(self):
        return os.path.join(self.config.get("BASE_URL"))

    def gen_theme_url(self):
        return os.path.join(self.config.get('STATIC_BASE_URL'),
                            self.config.get('THEME_NAME'))
    
    def gen_libs_url(self):
        return self.config.get("LIBS_URL")
    
    def gen_id(self, relative_path):
        content_dir = self.config.get('CONTENT_DIR')
        page_id = relative_path.replace(content_dir+"/", '', 1).lstrip('/')
        return page_id
    
    def gen_page_url(self, relative_path):
        content_dir = self.config.get('CONTENT_DIR')
        content_ext = self.config.get('CONTENT_FILE_EXT')
        default_index_alias = self.config.get("DEFAULT_INDEX_ALIAS")
        
        if relative_path.endswith(content_ext):
            relative_path = os.path.splitext(relative_path)[0]
        front_page_content_path = "{}/{}".format(content_dir,
                                                 default_index_alias)
        if relative_path.endswith(front_page_content_path):
            len_index_str = len(default_index_alias)
            relative_path = relative_path[:-len_index_str]
 
        relative_url = relative_path.replace(content_dir, '', 1)
        url = os.path.join(self.config.get("BASE_URL"),
                           relative_url.lstrip('/'))
        return url
    
    def gen_page_alias(self, relative_path):
        content_ext = self.config.get('CONTENT_FILE_EXT')
        if relative_path.endswith(content_ext):
            relative_path = os.path.splitext(relative_path)[0]
        alias = relative_path.split('/')[-1]
        return alias

    def gen_excerpt(self, content, theme_meta):
        default_excerpt_length = self.config.get('DEFAULT_EXCERPT_LENGTH')
        excerpt_length = theme_meta.get('excerpt_length',
                                        default_excerpt_length)
                                        
        default_excerpt_ellipsis = self.config.get('DEFAULT_EXCERPT_ELLIPSIS')
        excerpt_ellipsis = theme_meta.get('excerpt_ellipsis',
                                          default_excerpt_ellipsis)
                                          
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
        content_ext = self.config.get('CONTENT_FILE_EXT')
        default_404_alias = self.config.get('DEFAULT_404_ALIAS')
        return "{}{}".format(default_404_alias, content_ext)

    @property
    def content_not_found_full_path(self):
        content_dir = self.config.get('CONTENT_DIR')
        return os.path.join(content_dir, self.content_not_found_relative_path)

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
        meta_string = {"meta": meta_string}
        self.run_hook("before_read_page_meta", meta_string=meta_string)
        
        def convert_data(x):
            if isinstance(x, dict):
                return dict((k.lower(), convert_data(v)) 
                             for k, v in x.iteritems())
            elif isinstance(x, list):
                return list([convert_data(i) for i in x])
            elif isinstance(x, str):
                return x.decode("utf-8")
            elif isinstance(x, (unicode, int, float, bool)) or x is None:
                return x
            else:
                try:
                    x = str(x).decode("utf-8")
                except Exception as e:
                    print e
                    pass
            return x
        
        yaml_data = yaml.safe_load(meta_string['meta'])
        headers = convert_data(yaml_data)
        self.run_hook("after_read_page_meta", headers=headers)
        return headers

    @staticmethod
    def parse_content(content_string):
        use_markdown = current_app.config.get("USE_MARKDOWN")
        if use_markdown:
            markdown_exts = current_app.config.get("MARKDOWN_EXTENSIONS", [])
            return markdown.markdown(content_string, markdown_exts)
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
        date_format = config.get('DEFAULT_DATE_FORMAT')
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
        base_url = self.config.get("BASE_URL")
        def process_menu_url(menu):
            for item in menu:
                link = item.get("link")
                if link and not url_validator(link):
                    item["url"] = os.path.join(base_url, link.strip('/'))
                else:
                    item["url"] = link
                item["nodes"] = process_menu_url(item.get("nodes",[]))
            return menu
        for menu in menus:
            menus[menu] = process_menu_url(menus[menu])
        return menus
    
    def get_taxonomies(self):
        taxs = self.config['SITE'].get("taxonomy",{})
        tax_dict = {}
        for k,v in taxs.iteritems():
            tax_dict[k] = {
                "title": v.get("title"),
                "alias": k,
                "content_types": v.get("content_types"),
                "terms": [
                    {
                        "alias": x.get("alias"),
                        "title": x.get("title"),
                        "priority": x.get("priority"),
                        "meta": x.get("meta",{}),
                        "taxonomy": k,
                        "updated": x.get("updated")
                    }
                    for x in v.get("terms", [])
                ]
            }
            # del terms[tax["alias"]]
        
        return tax_dict
        
        
    def get_pages(self):
        config = self.config
        content_dir = config.get('CONTENT_DIR')
        content_ext = config.get('CONTENT_FILE_EXT')
        charset = config.get('CHARSET')
        files = self.get_files(content_dir, content_ext)
        invisible_page_list = self.config.get('INVISIBLE_PAGE_LIST')
        
        page_data_list = []
        for f in files:
            if f in invisible_page_list:
                continue

            relative_path = f.split(content_dir+"/", 1)[1]
            if relative_path.startswith("~") \
                or relative_path.startswith("#") \
                or relative_path in self.content_ignore_files:
                continue
            
            with open(f, "r") as fh:
                file_content = fh.read().decode(charset)
            meta_string, content_string = self.content_splitter(file_content)
            try:
                meta = self.parse_page_meta(meta_string)
            except Exception as e:
                e.current_file = f
                raise e
            data = self.parse_file_attrs(meta, f, content_string, False)
            self.run_hook("get_page_data", data=data, page_meta=meta.copy())
            page_data_list.append(data)

        # sortby
        theme_meta_options = self.view_ctx["theme_meta"].get("options")
        sort_desc = True
        sort_keys = ['-priority']
        sort_by = theme_meta_options.get("sortby", "updated")
        
        if isinstance(sort_by, (str, unicode)):
            sort_keys.append(sort_by)
        elif isinstance(sort_by, list):
            sort_keys = sort_keys + [key for key in sort_by 
                                     if isinstance(key, (str, unicode))]
        
        return sortby(page_data_list, sort_keys, reverse=sort_desc)

    #theme
    @property
    def theme_name(self):
        return self.config.get("THEME_NAME")

    def theme_path_for(self, tmpl_name):
        return "{}{}".format(tmpl_name, self.config.get('TEMPLATE_FILE_EXT'))
    
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
        data["id"] = self.gen_id(file_path)
        data["alias"] = self.gen_page_alias(file_path)
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
        self.view_ctx["libs_url"] = self.gen_libs_url()
        self.view_ctx["site_meta"] = config.get("SITE",{}).get("meta")
        self.view_ctx["theme_meta"] = config.get("THEME_META")
        self.view_ctx["sa"] = {
            'app':{
                'pv': 500,
                'vs': 500,
                'uv': 500,
                'ip': 500
            },
            'page': {
                'pv': 100,
                'vs': 100,
                'uv': 100,
                'ip': 100
            }
        }
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
        config = self.config
        status_code = 200
        is_not_found = False
        run_hook = self.run_hook
        
        #for pass intor hook
        file = {"path": None}
        file_content = {"content": None}
        
        # load
        self.load_metas()
        self.load_plugins(config.get("PLUGINS"))
        run_hook("plugins_loaded")
        
        current_app.debug = config.get("DEBUG")
        self.init_context()   
        
        run_hook("config_loaded", config=self.config)
        
        base_url = config.get("BASE_URL")
        charset = config.get('CHARSET')
        
        self.view_ctx["args"] = {k: v for k, v in request.args.iteritems()}
        self.view_ctx["request"] = request
        self.view_ctx["gfw"] = config.get("GFW", False)
        
        redirect_to = {"url": None}
        run_hook("request_url", request=request, redirect_to=redirect_to)
        site_redirect_url = helper_process_url(redirect_to.get("url"),
                                               config.get("BASE_URL"))
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
            file_content['content'] = f.read().decode(charset)
        
        if is_not_found:
            run_hook("after_404_load_content", file=file, content=file_content)
        run_hook("after_load_content", file=file, content=file_content)
        
        # parse file content
        tmp_file_content = file_content["content"]
        meta_string, content_string = self.content_splitter(tmp_file_content)
        
        
        try:
            page_meta = self.parse_page_meta(meta_string)
        except Exception as e:
            e.current_file = file["path"]
            raise e
        
        page_meta = self.parse_file_attrs(page_meta,
                                          file["path"],
                                          content_string)
        
        redirect_to = {"url": None}

        run_hook("single_page_meta",
                 page_meta=page_meta,
                 redirect_to=redirect_to)
        
        c_type = str(page_meta.get('type'))
        if c_type.startswith('_') and not redirect_to["url"]:
            default_404_alias = self.config.get("DEFAULT_404_ALIAS")
            redirect_to["url"] = os.path.join(base_url,
                                              default_404_alias)

        content_redirect_to = helper_process_url(redirect_to.get("url"),
                                                 base_url)
        if content_redirect_to and request.url != content_redirect_to:
            return redirect(redirect_to["url"], code=302)

        self.view_ctx["meta"] = page_meta
        
        page_content = dict()

        page_content['content'] = content_string
        run_hook("before_parse_content", content=page_content)
        
        page_content['content'] = self.parse_content(page_content['content'])
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
            default_template = config.get('DEFAULT_TEMPLATE')
            if is_not_found:
                abort(404)
            else:    
                template_file_path = self.theme_path_for(default_template)


        # make dotted able
        for k,v in self.view_ctx.iteritems():
            self.view_ctx[k] = helper_make_dotted_dict(v) 
        
        output = {}
        output['content'] = render_template(template_file_path,
                                            **self.view_ctx)
        run_hook("after_render", output=output)
        return make_content_response(output['content'], status_code)


class UploadView(MethodView):
    def get(self, filepath):
        
        filename = os.path.basename(filepath)

        try:
            mime_type = mimetypes.guess_type(filename)[0]
        except:
            mime_type = 'text'

        headers = dict()
        headers["Content-Type"] = mime_type

        base_set = ["origin", "accept", "content-type", "authorization"]
        headers["Access-Control-Allow-Headers"] = ", ".join(base_set)
        headers_options = "OPTIONS, HEAD, POST, PUT, DELETE"
        headers["Access-Control-Allow-Methods"] = headers_options
        headers["Access-Control-Allow-Origin"] = '*'
        headers["Access-Control-Max-Age"] = 60 * 60 * 24
        
        uploads_dir = current_app.config.get("UPLOADS_DIR")
        send_file = send_from_directory(uploads_dir, filepath)
        response = make_response(send_file)
        response.headers = headers
        return response


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
app.static_url_path = app.config.get("STATIC_BASE_URL")

# extend jinja
app.jinja_env.autoescape = False
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.jinja_env.add_extension('jinja2.ext.i18n')
app.jinja_env.add_extension('jinja2.ext.do')
app.jinja_env.add_extension('jinja2.ext.with_')
app.jinja_env.install_gettext_callables(gettext, ngettext, newstyle=True)


# routes
app.add_url_rule(app.static_url_path + '/<path:filename>',
    view_func=app.send_static_file, endpoint='static')

app.add_url_rule("/", defaults={"_": ""},
    view_func=ContentView.as_view("index"))

app.add_url_rule("/<path:_>", 
    view_func=ContentView.as_view("content"))
    
app.add_url_rule("/{}/<path:filepath>".format(app.config.get("UPLOADS_DIR")),
    view_func=UploadView.as_view("uploads"))


# @app.before_first_request
# def before_first_request():
#


@app.before_request
def before_request():
    load_config(current_app)
    if request.path.strip("/") in current_app.config.get('SYS_ICON_LIST'):
        abort(404)
    
    base_url = current_app.config.get("BASE_URL")
    base_path = current_app.config.get("BASE_PATH")
    uploads_dir = current_app.config.get("UPLOADS_DIR")
    
    g.curr_base_url = base_url
    g.curr_base_path = base_path
    g.request_path = request.path.replace(base_path, '', 1)
    g.static_host = os.path.join(base_url, uploads_dir)
    
    if current_app.debug:
        # change template folder
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
    return make_response(err_html_msg, 500)


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