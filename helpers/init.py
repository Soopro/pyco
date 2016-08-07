# coding=utf8
import os
import json
from types import ModuleType
from flask import g, current_app
from utils.file import check_file_exists
import re
import markdown
import json
import yaml
from hashlib import sha1
from utils.misc import (url_validator,
                         sortedby,
                         parse_args,
                         now)


def load_config(app, config_name="config.py"):
    app.config.from_pyfile(config_name)
    app.config.setdefault("DEBUG", False)
    app.config.setdefault("BASE_URL", "/")
    app.config.setdefault("BASE_PATH", "")
    app.config.setdefault("LIBS_URL", "http://libs.soopro.com")
    app.config.setdefault("PLUGINS", [])
    app.config.setdefault("IGNORE_FILES", [])
    app.config.setdefault("INVISIBLE_PAGE_LIST", [])
    app.config.setdefault("THEME_NAME", "default")
    app.config.setdefault("HOST", "0.0.0.0")
    app.config.setdefault("PORT", 5500)
    app.config.setdefault("SITE", {})
    app.config.setdefault("THEME_META", {})
    app.config.setdefault("CHARSET", "utf8")
    app.config.setdefault("SYS_ICON_LIST", [])

    app.config.setdefault("MAX_MODE_TYPES", ["ws"])
    app.config.setdefault("PLUGIN_DIR", "plugins")
    app.config.setdefault("THEMES_DIR", "themes")
    app.config.setdefault("TEMPLATE_FILE_EXT", ".html")
    app.config.setdefault("TPL_FILE_EXT", ".tpl")

    app.config.setdefault("DEFAULT_SITE_META_FILE", "site.json")
    app.config.setdefault("DEFAULT_THEME_META_FILE", "config.json")

    app.config.setdefault("DEFAULT_TEMPLATE", "index")

    app.config.setdefault("DEFAULT_DATE_FORMAT", "%Y-%m-%d")
    app.config.setdefault("DEFAULT_EXCERPT_LENGTH", 162)
    app.config.setdefault("DEFAULT_EXCERPT_ELLIPSIS", "&hellip;")

    app.config.setdefault("STATIC_PATH", "static")
    app.config.setdefault("UPLOADS_DIR", "uploads")
    app.config.setdefault("CONTENT_DIR", "content")
    app.config.setdefault("CONTENT_FILE_EXT", ".md")
    app.config.setdefault("DEFAULT_INDEX_SLUG", "index")
    app.config.setdefault("DEFAULT_404_SLUG", "error_404")

    return


def load_metas(config):
    theme_meta_file = os.path.join(config.get('THEMES_DIR'),
                                   config.get('THEME_NAME'),
                                   config.get('DEFAULT_THEME_META_FILE'))
    theme_meta = open(theme_meta_file)
    try:
        config['THEME_META'] = json.load(theme_meta)
    except Exception as e:
        err_msg = "Load Theme Meta faild: {}".format(str(e))
        raise Exception(err_msg)
    theme_meta.close()

    site_file = os.path.join(config.get('CONTENT_DIR'),
                             config.get('DEFAULT_SITE_META_FILE'))

    site_data = open(site_file)
    try:
        config['SITE'] = json.load(site_data)
        site_meta = config['SITE'].get("meta", {})
        g.curr_app = {
            "locale": site_meta.get("locale", u'en_US')
        }
    except Exception as e:
        err_msg = "Load Site Meta faild: {}".format(str(e))
        raise Exception(err_msg)
    site_data.close()


def load_plugins(plugins):
    loaded_plugins = []
    for module_or_module_name in plugins:
        if type(module_or_module_name) is ModuleType:
            loaded_plugins.append(module_or_module_name)
        elif isinstance(module_or_module_name, basestring):
            try:
                module = __import__(module_or_module_name)
            except ImportError as err:
                raise err
            loaded_plugins.append(module)
    return loaded_plugins


# common funcs
def get_file_path(config, url):
    content_dir = config.get('CONTENT_DIR')
    content_ext = config.get('CONTENT_FILE_EXT')
    default_index_slug = config.get("DEFAULT_INDEX_SLUG")

    base_path = os.path.join(content_dir, url[1:]).rstrip("/")
    file_name = "{}{}".format(base_path, content_ext)
    if check_file_exists(file_name):
        return file_name

    tmp_fname = "{}{}".format(default_index_slug, content_ext)
    file_name = os.path.join(base_path, tmp_fname)
    if check_file_exists(file_name):
        return file_name
    return None


def gen_base_url(config):
    return config.get("BASE_URL")


def gen_theme_url(config):
    return "{}/{}/{}".format(config.get("BASE_URL"),
                             config.get('STATIC_PATH'),
                             config.get('THEME_NAME'))


def gen_libs_url(config):
    return config.get("LIBS_URL")


def gen_api_baseurl(config):
    return config.get("API_URL")


def gen_id(config, relative_path):
    content_dir = config.get('CONTENT_DIR')
    page_id = relative_path.replace(content_dir + "/", '', 1).lstrip('/')
    return page_id


def gen_page_url(config, relative_path):
    content_dir = config.get('CONTENT_DIR')
    content_ext = config.get('CONTENT_FILE_EXT')
    default_index_slug = config.get("DEFAULT_INDEX_SLUG")

    if relative_path.endswith(content_ext):
        relative_path = os.path.splitext(relative_path)[0]
    front_page_content_path = "{}/{}".format(content_dir,
                                             default_index_slug)
    if relative_path.endswith(front_page_content_path):
        len_index_str = len(default_index_slug)
        relative_path = relative_path[:-len_index_str]

    relative_url = relative_path.replace(content_dir, '', 1)
    url = "{}/{}".format(config.get("BASE_URL"),
                         relative_url.lstrip('/'))
    return url


def gen_page_slug(config, relative_path):
    content_ext = config.get('CONTENT_FILE_EXT')
    if relative_path.endswith(content_ext):
        relative_path = os.path.splitext(relative_path)[0]
    slug = relative_path.split('/')[-1]
    return slug


def gen_excerpt(config, content, opts):
    default_excerpt_length = config.get('DEFAULT_EXCERPT_LENGTH')
    excerpt_length = opts.get('excerpt_length',
                              default_excerpt_length)
    default_excerpt_ellipsis = config.get('DEFAULT_EXCERPT_ELLIPSIS')
    excerpt_ellipsis = opts.get('excerpt_ellipsis',
                                default_excerpt_ellipsis)

    excerpt = re.sub(r'<[^>]*?>', '', content).strip()
    if excerpt:
        excerpt = u" ".join(excerpt.split())
        excerpt = excerpt[0:excerpt_length] + excerpt_ellipsis
    return excerpt


def content_not_found_relative_path(config):
    content_ext = config.get('CONTENT_FILE_EXT')
    default_404_slug = config.get('DEFAULT_404_SLUG')
    return ["{}{}".format(default_404_slug, content_ext)]


def content_not_found_full_path(config):
    content_dir = config.get('CONTENT_DIR')
    return os.path.join(content_dir, content_not_found_relative_path)


def content_ignore_files(config):
    base_files = content_not_found_relative_path(config)
    base_files.extend(config.get("IGNORE_FILES"))
    return base_files


def content_splitter(file_content):
    pattern = r"(\n)*/\*(\n)*(?P<meta>(.*\n)*)\*/(?P<content>(.*(\n)?)*)"
    re_pattern = re.compile(pattern)
    m = re_pattern.match(file_content)
    if m is None:
        return "", ""
    return m.group("meta"), m.group("content")


def parse_page_meta(plugins, meta_string):
    meta_string = {"meta": meta_string}
    run_hook(plugins, "before_read_page_meta", meta_string=meta_string)

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
    run_hook(plugins, "after_read_page_meta", headers=headers)
    return headers


def parse_content(content_string):
    use_markdown = current_app.config.get("USE_MARKDOWN")
    if use_markdown:
        markdown_exts = current_app.config.get("MARKDOWN_EXTENSIONS", [])
        return markdown.markdown(content_string, markdown_exts)
    else:
        return content_string


def generate_etag(content_file_full_path):
    file_stat = os.stat(content_file_full_path)
    base = "{mtime:0.0f}_{size:d}_{fpath}".format(
        mtime=file_stat.st_mtime,
        size=file_stat.st_size,
        fpath=content_file_full_path
    )

    return sha1(base).hexdigest()


def get_files(base_dir, ext):
    all_files = []
    for root, directory, files in os.walk(base_dir):
        file_full_paths = [
            os.path.join(root, f)
            for f in filter(lambda x: x.endswith(ext), files)
        ]
        all_files.extend(file_full_paths)
    return all_files


def get_menus(config):
    menus = config['SITE'].get("menus", {})
    base_url = config.get("BASE_URL")

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


def get_taxonomies(config):
    taxs = config['SITE'].get("taxonomies", {})
    tax_dict = {}
    for k, v in taxs.iteritems():
        tax_dict[k] = {
            "title": v.get("title"),
            "slug": k,
            "content_types": v.get("content_types"),
            "terms": [
                {
                    "key": x.get("key", u''),
                    "title": x.get("title", u''),
                    "class": x.get("class", u''),
                    "meta": x.get("meta", {}),
                    "nodes": x.get("nodes", []),
                }
                for x in v.get("terms", [])
            ]
        }

    return tax_dict


def get_pages(config, view_ctx, plugins):
    content_dir = config.get('CONTENT_DIR')
    content_ext = config.get('CONTENT_FILE_EXT')
    charset = config.get('CHARSET')
    files = get_files(content_dir, content_ext)
    invisible_slugs = config.get('INVISIBLE_SLUGS')

    page_data_list = []
    for f in files:
        if gen_page_slug(config, f) in invisible_slugs:
            continue

        relative_path = f.split(content_dir + "/", 1)[1]
        if relative_path.startswith("~") or \
           relative_path.startswith("#") or \
           relative_path in content_ignore_files(config):
            continue

        with open(f, "r") as fh:
            file_content = fh.read().decode(charset)
        meta_string, content_string = content_splitter(file_content)
        try:
            meta = parse_page_meta(plugins, meta_string)
        except Exception as e:
            e.current_file = f
            raise e
        data = parse_file_attrs(meta, f, content_string, config, view_ctx, False)
        run_hook(plugins, "get_page_data", data=data, page_meta=meta.copy())
        page_data_list.append(data)

    # sortedby
    theme_meta_options = view_ctx["theme_meta"].get("options")
    sort_desc = True
    sort_keys = ['-priority']
    sort_by = theme_meta_options.get("sortby", "updated")

    if isinstance(sort_by, basestring):
        sort_keys.append(sort_by)
    elif isinstance(sort_by, list):
        sort_keys = sort_keys + [key for key in sort_by
                                 if isinstance(key, basestring)]

    return sortedby(page_data_list, sort_keys, reverse=sort_desc)


def theme_name(config):
    return config.get("THEME_NAME")


def theme_path_for(config, tmpl_name):
    return "{}{}".format(tmpl_name, config.get('TEMPLATE_FILE_EXT'))


def theme_absolute_path_for(tmpl_path):
    return os.path.join(current_app.root_path,
                        current_app.template_folder,
                        tmpl_path)


def parse_file_attrs(meta, file_path, content_string, config,  view_ctx,
                     escape_content=True):

    data = dict()
    for m in meta:
        data[m] = meta[m]
    data["id"] = gen_id(config, file_path)
    data["slug"] = gen_page_slug(config, file_path)
    data["url"] = gen_page_url(config, file_path)
    data["title"] = meta.get("title", u"")
    data["priority"] = meta.get("priority", 0)
    data["author"] = meta.get("author", u"")
    # data['status'] = meta.get('status') # define by plugin
    # data['type'] = meta.get('type') # define by plugin
    data["updated"] = meta.get("updated", 0)
    data["date"] = meta.get("date", u"")

    content = parse_content(content_string)
    opts = view_ctx["theme_meta"].get('options', {})
    data["excerpt"] = gen_excerpt(config, content, opts)
    des = meta.get("description")
    data["description"] = data["excerpt"] if not des else des

    if not escape_content:
        data["content"] = content
    data["creation"] = int(os.path.getmtime(file_path))
    data["updated"] = int(os.path.getctime(file_path))
    return data


def init_context(request, config, include_request=True):
    # env context
    site_meta = config.get("SITE", {}).get("meta", {})
    view_ctx = dict()
    view_ctx["app_id"] = site_meta.get('id', 'pyco_app')
    view_ctx["base_url"] = gen_base_url(config)
    view_ctx["theme_url"] = gen_theme_url(config)
    view_ctx["libs_url"] = gen_libs_url(config)
    view_ctx["api_baseurl"] = gen_api_baseurl(config)
    view_ctx["site_meta"] = site_meta
    view_ctx["theme_meta"] = config.get("THEME_META")

    view_ctx["now"] = now()

    if include_request:
        view_ctx["args"] = parse_args()
        view_ctx["request"] = {
            "remote_addr": request.remote_addr,
            "path": request.path,
            "url": request.url,
            "args": parse_args(),
        }

    # menu
    menu = get_menus(config)
    view_ctx["menu"] = menu

    # taxonomy
    taxonomy = get_taxonomies(config)
    view_ctx["tax"] = view_ctx["taxonomy"] = taxonomy

    return view_ctx


def run_hook(plugins, hook_name, **references):
    for plugin_module in plugins:
        func = plugin_module.__dict__.get(hook_name)
        if callable(func):
            func(**references)
    return
