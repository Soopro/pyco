# coding=utf-8
from __future__ import absolute_import

from flask import current_app, g
import os
import re
import markdown
from utils.validators import url_validator
from utils.misc import parse_int, match_cond, sortedby


def query_by_files(attrs, sortby=[], limit=1, offset=0, priority=True):
    # query
    files = _query(g.files, attrs)
    # sorting
    sorting = _sorting(files, sortby)

    limit = parse_int(limit, 1)
    offset = parse_int(offset, 0)

    if sorting:
        ids = [item['_id'] for item in sorting[offset:offset + limit]]
        order_dict = {_id: index for index, _id in enumerate(ids)}
        files = [f for f in files if f['_id'] in ids]
        files.sort(key=lambda x: order_dict[x["_id"]])
    else:
        files = files[offset:offset + limit]
    return files


def count_by_files(attrs):
    return len(_query(g.files, attrs))


def find_content_file(path, default_type=u'page'):
    type_slug = path.get('content_type', default_type)
    for f in g.files:
        if f['slug'] == path['slug'] and f['content_type'] == type_slug:
            return f
    return None


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


def read_page_metas(page, content, options, current_id=None):
    excerpt = make_file_excerpt(content)

    data = dict()
    meta = page.get("meta")
    for m in meta:
        data[m] = meta[m]
    data['id'] = unicode(page['_id'])
    data['app_id'] = unicode(page['app_id'])
    data['slug'] = page['slug']
    data['type'] = data['content_type'] = page['content_type']
    data['updated'] = page['updated']
    data['creation'] = page['creation']

    data['parent'] = page['parent']
    data['priority'] = page['priority']
    data['status'] = page['status']
    data['date'] = page['date']

    data['template'] = page['template']
    data['taxonomy'] = page['taxonomy']
    data['tags'] = page['tags']

    excerpt_len = options.get('excerpt_length')
    ellipsis = options.get('excerpt_ellipsis')
    data['excerpt'] = gen_file_excerpt(excerpt, excerpt_len, ellipsis)

    data['description'] = meta.get('description') or data['excerpt']
    data['url'] = gen_page_url(page['content_type'], page['slug'])

    # content marks
    config = current_app.config
    if data['slug'] == config.get('DEFAULT_INDEX_SLUG'):
        data['is_front'] = True
    if data['slug'] == config.get('DEFAULT_404_SLUG'):
        data['is_404'] = True
    if unicode(data['id']) == unicode(current_id):
        data['is_current'] = True

    return data


def gen_page_url(content_type_slug, file_slug):
    return "{}/{}/{}".format(g.curr_base_url, content_type_slug, file_slug)


def make_file_excerpt(content, length=600):
    excerpt = re.sub(r'<[^>]*?>', '', content).strip()
    return excerpt[:length].strip()


def gen_file_excerpt(excerpt, excerpt_length, ellipsis):
    excerpt_length = parse_int(excerpt_length, 162, True)
    if isinstance(ellipsis, basestring):
        excerpt_ellipsis = ellipsis
    else:
        excerpt_ellipsis = u'&hellip;'

    if excerpt:
        excerpt = u" ".join(excerpt.split())  # remove empty strings.
        excerpt = u"{}{}".format(excerpt[0:excerpt_length], excerpt_ellipsis)
    return excerpt


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


# query contents
def count_matched(attrs):
    pass


# taxonomy
def helper_wrap_taxonomy(taxonomies):
    if not taxonomies:
        return {}

    tax_dict = {}

    def _parse_term(term, tax, content_types):
        attrs = [
            {'type': content_types},
            {'taxonomy.{}'.format(tax["slug"]): term.get('key')}
        ]
        term['count'] = count_matched(attrs)
        return term

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


# helpers
def _query(files, attrs):
    SHORT_FIELD_KEYS = current_app.config.get('SHORT_FIELD_KEYS')
    QUERYABLE_FIELD_KEYS = current_app.config.get('QUERYABLE_FIELD_KEYS')

    for attr in attrs[:5]:  # max fields key is 5
        opposite = False
        force = False
        attr_key = None
        attr_value = ''

        if isinstance(attr, basestring):
            attr_key = attr.lower()
        elif isinstance(attr, dict):
            opposite = bool(attr.pop('not', False))
            force = bool(attr.pop('force', False))
            if attr:
                attr_key = attr.keys()[0]
                attr_value = attr[attr_key]
            else:
                continue

        if attr_key is None:
            continue

        attr_key = SHORT_FIELD_KEYS.get(attr_key, attr_key)
        if attr_key not in QUERYABLE_FIELD_KEYS \
           and '.' not in attr_key:
            attr_key = "meta.{}".format(attr_key)
        files = [f for f in files
                 if match_cond(f, attr_key, attr_value, force, opposite)]

    return files


def _sorting(files, sort_keys):
    SHORT_FIELD_KEYS = current_app.config.get('SHORT_FIELD_KEYS')
    SORTABLE_FIELD_KEYS = current_app.config.get('SORTABLE_FIELD_KEYS')
    if not sort_keys:
        sorts_list = [("updated", -1)]
    else:
        sorts_list = []
        for sort in sort_keys[:5]:  # max sort keys is 5
            if isinstance(sort, basestring):
                if sort.startswith('+'):
                    key = sort.lstrip('+')
                    direction = 1
                else:
                    key = sort.lstrip('-')
                    direction = -1
            elif isinstance(sort, tuple):
                key = sort[0]
                direction = sort[1]
            else:
                continue

            # format to match the structure
            if key in SHORT_FIELD_KEYS:
                key = SHORT_FIELD_KEYS.get(key)

            # remove duplicate key, and append end of the sorts list.
            # DO NOT use set, because the only check key.
            for idx, sort in enumerate(sorts_list):
                if sort and key == sort[0]:
                    sorts_list[idx] = None
            sorts_list.append((key, direction))

        sorts_list = [sort for sort in sorts_list if sort]

    sorting = []
    for f in files:
        new_entry = {"_id": f["_id"]}
        for sort in sorts_list:
            key = sort[0]
            if key in SORTABLE_FIELD_KEYS:
                new_entry[key] = f[key]
            else:
                new_entry[key] = f['meta'].get(key)
        sorting.append(new_entry)

    return sortedby(sorting, sorts_list)
