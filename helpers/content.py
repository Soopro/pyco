# coding=utf-8
from __future__ import absolute_import

from flask import current_app, request
import os
import re
import yaml
import markdown

from utils.misc import (url_validator,
                        sortedby,
                        parse_args,
                        now)


def get_files(base_dir, ext):
    all_files = []
    for root, directory, files in os.walk(base_dir):
        file_full_paths = [
            os.path.join(root, f)
            for f in filter(lambda x: x.endswith(ext), files)
        ]
        all_files.extend(file_full_paths)
    return all_files


def parse_page_meta(meta_string):
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
    yaml_data = yaml.safe_load(meta_string)
    headers = convert_data(yaml_data)
    return headers


def parse_content(content_string):
    use_markdown = current_app.config.get("USE_MARKDOWN")
    if use_markdown:
        markdown_exts = current_app.config.get("MARKDOWN_EXTENSIONS", [])
        return markdown.markdown(content_string, markdown_exts)
    else:
        return content_string


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


def get_file_path(file_slug, content_type_slug):
    content_dir = current_app.config.get('CONTENT_DIR')
    content_ext = current_app.config.get('CONTENT_FILE_EXT')

    if content_type_slug == 'page':
        scope = os.path.join(content_dir, file_slug)
    else:
        scope = os.path.join(content_dir, content_type_slug, file_slug)
    file_path = "{}{}".format(scope, content_ext)
    if os.path.isfile(file_path):
        return file_path
    return None


def get_pages():
    config = current_app.config
    content_dir = config.get('CONTENT_DIR')
    content_ext = config.get('CONTENT_FILE_EXT')
    files = get_files(content_dir, content_ext)
    invisible_slugs = config.get('INVISIBLE_SLUGS')
    theme_meta_options = config['THEME_META'].get('options', {})

    page_data_list = []
    for f in files:
        if gen_page_slug(f) in invisible_slugs:
            continue

        relative_path = f.split(content_dir + "/", 1)[1]
        if relative_path.startswith("~") or relative_path.startswith("#"):
            continue

        with open(f, "r") as fh:
            file_content = fh.read().decode(config.get('CHARSET', 'utf-8'))
        meta_string, content_string = content_splitter(file_content)
        try:
            meta = parse_page_meta(meta_string)
        except Exception as e:
            e.current_file = f
            raise e
        data = parse_file_metas(meta, f, content_string, theme_meta_options)
        page_data_list.append(data)

    # sortedby
    sort_desc = True
    sort_keys = ['-priority']
    sort_by = theme_meta_options.get("sortby", "updated")

    if isinstance(sort_by, basestring):
        sort_keys.append(sort_by)
    elif isinstance(sort_by, list):
        sort_keys = sort_keys + [key for key in sort_by
                                 if isinstance(key, basestring)]

    return sortedby(page_data_list, sort_keys, reverse=sort_desc)


def parse_file_metas(meta, file_path, content_string, options):
    data = dict()
    for m in meta:
        data[m] = meta[m]
    data["id"] = gen_id(file_path)
    data["slug"] = gen_page_slug(file_path)
    data["url"] = gen_page_url(file_path)
    data["title"] = meta.get("title", u"")
    data["priority"] = meta.get("priority", 0)
    data["author"] = meta.get("author", u"")
    # data['status'] = meta.get('status') # define by plugin
    # data['type'] = meta.get('type') # define by plugin
    data["updated"] = meta.get("updated", 0)
    data["date"] = meta.get("date", u"")

    content = parse_content(content_string)
    data["excerpt"] = gen_excerpt(content, options)
    des = meta.get("description")
    data["description"] = data["excerpt"] if not des else des
    data["content"] = content
    data["creation"] = int(os.path.getmtime(file_path))
    data["updated"] = int(os.path.getctime(file_path))
    return data


def init_context(include_request=True):
    config = current_app.config
    # env context
    site_meta = config.get("SITE", {}).get("meta", {})
    view_ctx = dict()
    view_ctx["app_id"] = site_meta.get('id', 'pyco_app')
    view_ctx["base_url"] = config.get("BASE_URL", '')
    view_ctx["theme_url"] = config.get("THEME_URL", '')
    view_ctx["libs_url"] = config.get("LIBS_URL", '')
    view_ctx["api_baseurl"] = config.get("API_URL", '')
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


def gen_id(relative_path):
    content_dir = current_app.config.get('CONTENT_DIR')
    page_id = relative_path.replace(content_dir + "/", '', 1).lstrip('/')
    return page_id


def gen_page_url(relative_path):
    content_dir = current_app.config.get('CONTENT_DIR')
    content_ext = current_app.config.get('CONTENT_FILE_EXT')
    default_index_slug = current_app.config.get("DEFAULT_INDEX_SLUG")

    if relative_path.endswith(content_ext):
        relative_path = os.path.splitext(relative_path)[0]
    front_page_content_path = "{}/{}".format(content_dir,
                                             default_index_slug)
    if relative_path.endswith(front_page_content_path):
        len_index_str = len(default_index_slug)
        relative_path = relative_path[:-len_index_str]

    relative_url = relative_path.replace(content_dir, '', 1)
    url = "{}/{}".format(current_app.config.get("BASE_URL"),
                         relative_url.lstrip('/'))
    return url


def gen_page_slug(relative_path):
    content_ext = current_app.config.get('CONTENT_FILE_EXT')
    if relative_path.endswith(content_ext):
        relative_path = os.path.splitext(relative_path)[0]
    slug = relative_path.split('/')[-1]
    return slug


def gen_excerpt(content, opts):
    default_excerpt_length = current_app.config.get('DEFAULT_EXCERPT_LENGTH')
    excerpt_length = opts.get('excerpt_length', default_excerpt_length)
    default_ellipsis = current_app.config.get('DEFAULT_EXCERPT_ELLIPSIS')
    excerpt_ellipsis = opts.get('excerpt_ellipsis', default_ellipsis)

    excerpt = re.sub(r'<[^>]*?>', '', content).strip()
    if excerpt:
        excerpt = u" ".join(excerpt.split())
        excerpt = excerpt[0:excerpt_length] + excerpt_ellipsis
    return excerpt


def content_not_found_full_path():
    content_dir = current_app.config.get('CONTENT_DIR')
    file_404 = "{}{}".format(current_app.config.get('DEFAULT_404_SLUG'),
                             current_app.config.get('CONTENT_FILE_EXT'))
    return os.path.join(content_dir, file_404)


def content_splitter(file_content):
    pattern = r"(\n)*/\*(\n)*(?P<meta>(.*\n)*)\*/(?P<content>(.*(\n)?)*)"
    re_pattern = re.compile(pattern)
    m = re_pattern.match(file_content)
    if m is None:
        return "", ""
    return m.group("meta"), m.group("content")
