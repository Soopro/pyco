#coding=utf-8
from __future__ import absolute_import

from flask import current_app, request
from flask.views import MethodView

import os, re, markdown, json, yaml

from hashlib import sha1
from types import ModuleType
from datetime import datetime

from helpers import (url_validator,
                     sortedby,
                     parse_args)



class BaseView(MethodView):

    def __init__(self):
        super(BaseView, self).__init__()
        self.plugins = []
        self.config = current_app.config
        self.type = None
        self.max_mode = True
        self.view_ctx = dict()


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
        default_index_slug = self.config.get("DEFAULT_INDEX_SLUG")

        base_path = os.path.join(content_dir, url[1:]).rstrip("/")
        file_name = "{}{}".format(base_path, content_ext)
        if self.check_file_exists(file_name):
            return file_name

        tmp_fname = "{}{}".format(default_index_slug, content_ext)
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
        default_index_slug = self.config.get("DEFAULT_INDEX_SLUG")

        if relative_path.endswith(content_ext):
            relative_path = os.path.splitext(relative_path)[0]
        front_page_content_path = "{}/{}".format(content_dir,
                                                 default_index_slug)
        if relative_path.endswith(front_page_content_path):
            len_index_str = len(default_index_slug)
            relative_path = relative_path[:-len_index_str]

        relative_url = relative_path.replace(content_dir, '', 1)
        url = os.path.join(self.config.get("BASE_URL"),
                           relative_url.lstrip('/'))
        return url

    def gen_page_slug(self, relative_path):
        content_ext = self.config.get('CONTENT_FILE_EXT')
        if relative_path.endswith(content_ext):
            relative_path = os.path.splitext(relative_path)[0]
        slug = relative_path.split('/')[-1]
        return slug

    def gen_excerpt(self, content, opts):
        default_excerpt_length = self.config.get('DEFAULT_EXCERPT_LENGTH')
        excerpt_length = opts.get('excerpt_length',
                                  default_excerpt_length)
        default_excerpt_ellipsis = self.config.get('DEFAULT_EXCERPT_ELLIPSIS')
        excerpt_ellipsis = opts.get('excerpt_ellipsis',
                                    default_excerpt_ellipsis)

        excerpt = re.sub(r'<[^>]*?>', '', content).strip()
        if excerpt:
            excerpt = u" ".join(excerpt.split())
            excerpt = excerpt[0:excerpt_length]+excerpt_ellipsis
        return excerpt

    @staticmethod
    def check_file_exists(file_full_path):
        return os.path.isfile(file_full_path)

    # content
    @property
    def content_not_found_relative_path(self):
        content_ext = self.config.get('CONTENT_FILE_EXT')
        default_404_slug = self.config.get('DEFAULT_404_SLUG')
        return "{}{}".format(default_404_slug, content_ext)

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
        menus = self.config['SITE'].get("menus", {})
        base_url = self.config.get("BASE_URL")

        def process_menu_url(menu):
            for item in menu:
                link = item.get("link", "")
                if not link or url_validator(link):
                    item["url"] = link
                elif link.startswith('/'):
                    item["url"] = os.path.join(base_url, link.strip('/'))
                else:
                    item["url"] = link.rstrip('/')
                item["nodes"] = process_menu_url(item.get("nodes", []))
            return menu

        for menu in menus:
            menus[menu] = process_menu_url(menus[menu])
        return menus

    def get_taxonomies(self):
        taxs = self.config['SITE'].get("taxonomies",{})
        tax_dict = {}
        for k,v in taxs.iteritems():
            tax_dict[k] = {
                "title": v.get("title"),
                "slug": k,
                "content_types": v.get("content_types"),
                "terms": [
                    {
                        "slug": x.get("slug"),
                        "title": x.get("title"),
                        "priority": x.get("priority"),
                        "meta": x.get("meta",{}),
                        "taxonomy": k,
                        "updated": x.get("updated")
                    }
                    for x in v.get("terms", [])
                ]
            }

        return tax_dict


    def get_pages(self):
        config = self.config
        content_dir = config.get('CONTENT_DIR')
        content_ext = config.get('CONTENT_FILE_EXT')
        charset = config.get('CHARSET')
        files = self.get_files(content_dir, content_ext)
        invisible_slugs = config.get('INVISIBLE_SLUGS')

        page_data_list = []
        for f in files:
            if f in invisible_slugs:
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

        # sortedby
        theme_meta_options = self.view_ctx["theme_meta"].get("options")
        sort_desc = True
        sort_keys = ['-priority']
        sort_by = theme_meta_options.get("sortby", "updated")

        if isinstance(sort_by, basestring):
            sort_keys.append(sort_by)
        elif isinstance(sort_by, list):
            sort_keys = sort_keys + [key for key in sort_by
                                     if isinstance(key, basestring)]

        return sortedby(page_data_list, sort_keys, reverse=sort_desc)

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
        data["slug"] = self.gen_page_slug(file_path)
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
        opts = self.view_ctx["theme_meta"].get('options', {})
        data["excerpt"] = self.gen_excerpt(content, opts)
        des = meta.get("description")
        data["description"] = data["excerpt"] if not des else des

        if not escape_content:
            data["content"] = content
        data["creation"] = int(os.path.getmtime(file_path))
        data["updated"] = int(os.path.getctime(file_path))
        return data


    # context
    def init_context(self, include_request = True):
        # env context
        config = self.config
        app_id = self.config['SITE'].get("app_id", "pyco_app")
        extension = self.config['SITE'].get("extension", {})
        self.view_ctx["app_id"] = app_id
        self.view_ctx["base_url"] = self.gen_base_url()
        self.view_ctx["theme_url"] = self.gen_theme_url()
        self.view_ctx["libs_url"] = self.gen_libs_url()
        self.view_ctx["site_meta"] = config.get("SITE",{}).get("meta")
        self.view_ctx["theme_meta"] = config.get("THEME_META")

        if include_request:
            self.view_ctx["args"] = parse_args()
            self.view_ctx["request"] = request

        # menu
        menu = self.get_menus()
        self.view_ctx["menu"] = menu

        # taxonomy
        taxonomy = self.get_taxonomies()
        self.view_ctx["tax"] = self.view_ctx["taxonomy"] = taxonomy

        return

    #hook
    def run_hook(self, hook_name, **references):
        for plugin_module in self.plugins:
            func = plugin_module.__dict__.get(hook_name)
            if callable(func):
                func(**references)
        return
