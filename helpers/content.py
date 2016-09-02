# coding=utf-8
from __future__ import absolute_import

from flask import current_app
import os
import re
import yaml
import markdown
from utils.validators import url_validator
from utils.misc import sortedby


def get_files(base_dir, ext):
    all_files = []
    for root, directory, files in os.walk(base_dir):
        file_full_paths = [
            os.path.join(root, f)
            for f in filter(lambda x: x.endswith(ext), files)
        ]
        all_files.extend(file_full_paths)
    return all_files


def parse_file_headers(meta_string):
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


def helper_get_file_path(file_slug, content_type_slug):
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
            meta = parse_file_headers(meta_string)
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

    excerpt = re.sub(r'<[^>]*?>', '', content[:600]).strip()
    if excerpt:
        excerpt = u" ".join(excerpt.split())
        excerpt = excerpt[0:excerpt_length] + excerpt_ellipsis
    return excerpt


def content_splitter(file_content):
    pattern = r"(\n)*/\*(\n)*(?P<meta>(.*\n)*)\*/(?P<content>(.*(\n)?)*)"
    re_pattern = re.compile(pattern)
    m = re_pattern.match(file_content)
    if m is None:
        return "", ""
    return m.group("meta"), m.group("content")


# menus
def helper_wrap_menu(menus, base_url):
    if not menus:
        return {}

    def process_menu_url(menu):
        for item in menu:
            link = item.get("link", "")
            if not link or url_validator(link):
                item["url"] = link
            elif link.startswith('/'):
                item["url"] = "{}/{}".format(base_url, link.strip('/'))
            else:
                item["url"] = link.rstrip('/')
            item["nodes"] = process_menu_url(item.get("nodes", []))
        return menu

    menu_dict = {}
    for menu in menus:
        nodes = menu.get("nodes", [])
        nodes = process_menu_url(nodes)
        menu_dict[menu.get("slug")] = nodes

    return menu_dict


# socials
def helper_wrap_socials(socials):
    """ socials json sample
    {
       "facebook":{
           "name":"Facebook",
           "url":"http://....",
           "code":"..."
       },
       "twitter":{
           "name":"Twitter",
           "url":"http://....",
           "code":"..."
       }
    }
    """
    if not socials:
        return []

    social_list = []

    if isinstance(socials, list):
        # directly append if is list
        social_list = [social for social in socials if social.get('key')]

    elif isinstance(socials, dict):
        # change to list if is dict
        def _make_key(k, v):
            v.update({"key": k})
            return v
        social_list = [_make_key(k, v) for k, v in socials.iteritems()]

    return social_list


# taxonomy
def helper_wrap_taxonomy(app, taxonomies):
    ContentFile = current_app.mongodb.ContentFile
    tax_dict = {}

    def _parse_term(term, app, content_types):
        key = term.get('key')
        attr = 'meta.taxonomy.{}'.format(tax["slug"])
        term['count'] = _count_terms(app['_id'], content_types, attr, key)
        return term

    def _count_terms(app_id, content_types, attr, key):
        if not key:
            return 0
        attrs = [
            {'type': content_types},
            {attr: key}
        ]
        return ContentFile.count_matched(app_id, attrs)

    for tax in taxonomies:
        content_types = tax.get("content_types", [])
        tax_dict[tax["slug"]] = {
            "title": tax.get("title"),
            "content_types": content_types,
            "terms": [_parse_term(term, tax, content_types)
                      for term in tax['terms']]
        }
    return tax_dict


# translates
def helper_wrap_translates(translates, locale):
    """ translates json sample
    {
       "zh_CN":{"name":"汉语","url":"http://....."},
       "en_US":{"name":"English","url":"http://....."}
    }
    """
    if not translates:
        return []

    trans_list = []
    lang = locale.split('_')[0]

    if isinstance(translates, list):
        # directly append if is list
        trans_list = [trans for trans in translates if trans.get('key')]

    elif isinstance(translates, dict):
        # change to list if is dict
        def _make_key(k, v):
            v.update({"key": k})
            return v
        trans_list = [_make_key(k, v) for k, v in translates.iteritems()]

    for trans in trans_list:
        trans_key = trans['key'].lower()
        if trans_key == locale.lower() or trans_key == lang.lower():
            trans["active"] = True

    return trans_list
