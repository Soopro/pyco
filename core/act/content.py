# coding=utf-8

from flask import current_app, Markup, g

import re
import markdown

from core.utils.validators import url_validator
from core.utils.misc import (parse_int,
                             match_cond,
                             sortedby,
                             parse_sortby,
                             process_slug,
                             gen_excerpt,
                             now)


def query_by_files(content_type=None, attrs=None, term=None, tag=None,
                   offset=0, limit=1, sortby=None):
    # query
    files = _query(content_type=content_type,
                   attrs=attrs,
                   term=term,
                   tag=tag)

    total_count = len(files)

    # sorting
    sorting = _sorting(files, parse_sortby(sortby))

    limit = parse_int(limit, 1, 1)
    offset = parse_int(offset, 0, 0)

    if sorting:
        ids = [item['_id'] for item in sorting[offset:offset + limit]]
        order_dict = {_id: index for index, _id in enumerate(ids)}
        files = [f for f in files if f['_id'] in ids]
        files.sort(key=lambda x: order_dict[x['_id']])
    else:
        files = files[offset:offset + limit]
    return files, total_count


# segments
def query_segments(app, type_slug, parent_slug):
    _config = app['theme_meta']
    _opts = _config.get('options', {})
    sortby = parse_sortby(_opts.get('sortby', 'updated'))
    tmpls = [process_slug(tmpl) for tmpl in _config.get('templates', [])
             if tmpl.startswith('^')]

    if tmpls:
        files = current_app.db.Document.find(type_slug)
        segments = [f for f in files if f['template'] in tmpls and
                    f['parent'] == parent_slug and f['status']]
        segments = sortedby(segments, [('priority', 1), sortby])[:60]
    else:
        segments = []
    return segments


# search
def search_by_files(keywords, content_type,
                    offset=0, limit=0, use_tags=True):
    files = current_app.db.Document.find(content_type)

    if not keywords:
        results = files
    else:
        results = []
        if isinstance(keywords, str):
            keywords = keywords.split()
        elif not isinstance(keywords, list):
            keywords = []

        def _search_match(keyword, f):
            if keyword in f['_keywords'] and f['status']:
                return True
            return False

        results = files
        for kw in keywords:
            results = [f for f in results if _search_match(kw, f)]

    limit = parse_int(limit, 1, 1)
    offset = parse_int(offset, 0, 0)

    return results[offset:offset + limit], len(results)


def find_content_file(type_slug, file_slug):
    return current_app.db.Document.find_one(file_slug, type_slug)


def find_404_content_file():
    error_404_slug = current_app.db.Document.ERROR404_SLUG
    return {
        '_id': '.id-error-404',
        'app_id': g.curr_app['_id'],
        'slug': error_404_slug,
        'template': error_404_slug,
        'content_type': '.h',
        'meta': {},
        'parent': '',
        'priority': 1,
        'date': '',
        'content': '',
        'excerpt': '',
        'tags': [],
        'terms': [],
        'updated': now(),
        'creation': now(),
        'status': 1,
    }


def parse_page_content(content_string):
    if current_app.config['USE_MARKDOWN']:
        markdown_exts = current_app.config['MARKDOWN_EXTENSIONS']
        content_string = markdown.markdown(content_string, markdown_exts)
    return Markup(content_string)


def parse_page_metas(page, current_id=None):
    data = dict()
    meta = page.get('meta')
    for m in meta:
        data[m] = meta[m]
    data['id'] = str(page['_id'])
    data['slug'] = page['slug']
    data['type'] = data['content_type'] = page['content_type']
    data['template'] = page['template']
    data['parent'] = page['parent']
    data['priority'] = page['priority']
    data['status'] = page['status']
    data['date'] = page['date']
    data['tags'] = page['tags']
    data['terms'] = page['terms']
    data['updated'] = page['updated']
    data['creation'] = page['creation']
    data['excerpt'] = page['excerpt']
    data['description'] = meta.get('description', '')
    data['url'] = gen_page_url(page)
    data['path'] = gen_page_path(page)

    # content marks
    if data['slug'] == current_app.db.Document.INDEX_SLUG:
        data['is_front'] = True
    if data['slug'] == current_app.db.Document.ERROR404_SLUG:
        data['is_404'] = True
    if str(data['id']) == str(current_id):
        data['is_current'] = True

    return data


def gen_file_excerpt(content, excerpt_length=600):
    return gen_excerpt(content, excerpt_length)


def gen_page_path(data, static_type='page', index='index'):
    slug = data.get('slug')
    if data['content_type'] == static_type:
        if slug == index:
            slug = ''
        path = '/{}'.format(slug)
    else:
        path = '/{}/{}'.format(data['content_type'], slug)
    return path


def gen_page_url(data, static_type='page', index='index'):
    slug = data.get('slug')
    if data.get('content_type') == static_type:
        if slug == index:
            slug = ''
        url = '{}/{}'.format(g.base_url, slug)
    else:
        url = '{}/{}/{}'.format(g.base_url, data['content_type'], slug)
    return url


# menus
def gen_wrap_menu(app, base_url=''):
    if not app['menus']:
        return {}

    def process_menu_url(menu):
        for item in menu:
            link = item.get('link', '')
            if link:
                if url_validator(link):
                    # url
                    item['url'] = link

                    # path
                    if link.startswith(base_url):
                        _path = link.replace(base_url, '').strip('/')
                        item['path'] = '/{}'.format(_path)
                    else:
                        item['path'] = ''

                    # hash
                    item['hash'] = ''
                else:
                    # url
                    item['url'] = '{}/{}'.format(base_url, link.strip('/'))

                    # path
                    item['path'] = '/{}'.format(link.strip('/'))

                    # hash
                    _relpath = re.sub(r'^[/#]*', '', link).strip()
                    if '#' in _relpath or item.get('fixed'):
                        item['hash'] = ''
                    else:
                        item['hash'] = '#{}'.format(_relpath)
            else:
                item['url'] = ''
                item['hash'] = ''
                item['path'] = ''

            # name
            item['name'] = item['name'] or item['key']

            # nodes
            item['nodes'] = process_menu_url(item.get('nodes', []))
        return menu

    menu_dict = {}
    for slug, nodes in app['menus'].items():
        nodes = process_menu_url(nodes)
        menu_dict[slug] = nodes
    return menu_dict


# category
def gen_wrap_category(app, included_term_keys=None):
    if not app['categories'] or not isinstance(app['categories'], dict):
        return None

    # `included_term_keys` could be None or some other empty data.
    # as long as this parameter is given, result terms must limited.
    if included_term_keys is False:
        included_term_keys = None  # reset to None for further usage.
    elif not isinstance(included_term_keys, list):
        included_term_keys = []

    def __check_term(term):
        if not term.get('key') or term.get('status') == 0:
            return False
        elif isinstance(included_term_keys, list):
            return term['key'] in included_term_keys
        else:
            return True

    category = app['categories']
    raw_terms = [term for term in category.get('terms', [])
                 if __check_term(term)]
    terms = _sort_terms(raw_terms, True)
    terms_dict = {term['key']: term for term in _sort_terms(raw_terms)}

    return {
        'name': category.get('name'),
        'content_types': category.get('content_types', []),
        'terms': terms,
        'terms_dict': terms_dict,
    }


def _sort_terms(terms, included_term_keys=None, nest_output=True):
    if not terms or not isinstance(terms, list):
        return []

    term_list = [{
        'key': term['key'],
        'parent': term.get('parent', ''),
        'meta': term.get('meta', {}),
        'priority': term.get('priority', 1)
    } for term in terms]

    term_list = sortedby(term_list, [('priority', 1)])

    if nest_output:
        output_terms = []
        children = []
        for term in term_list:
            if term['parent']:
                children.append(term)
            else:
                output_terms.append(term)
        for term in output_terms:
            _rest_children = []
            for child in children:
                if child['parent'] == term['key']:
                    if term.get('nodes'):
                        term['nodes'].append(child)
                    else:
                        term['nodes'] = [child]
                else:
                    _rest_children.append(child)
            children = _rest_children
        if children:
            # incase there is more children left
            output_terms += [{
                'key': child['key'],
                'parent': '',  # clear parent
                'meta': child['meta']
            } for child in children]
    else:
        output_terms = term_list

    return output_terms


# slot
def gen_wrap_slot(app):
    if not app['slots']:
        return {}
    slots_map = {}
    for k, v in app['slots'].items():
        status = bool(v.get('status', True))
        if status:
            slots_map[k] = {
                'name': v.get('name', ''),
                'src': v.get('src', ''),
                'route': v.get('route', ''),
                'scripts': v.get('scripts', ''),
                'data': v.get('data', {}),
            }
    return slots_map


# languages
def gen_wrap_languages(languages, locale):
    """ languages data sample
    [
        {'key': 'zh_CN', 'name': '汉语', 'url': 'http://.....'},
        {'key': 'en_US', 'name': 'English', 'url': 'http://.....'}
    ]
    """

    if not languages or not isinstance(languages, list):
        return []

    lang_list = []
    lang = locale.split('_')[0]
    matched_pairs = (locale.lower(), lang.lower())

    for lang in languages:
        if not lang.get('key'):
            continue
        lang_list.append({
            'key': lang['key'],
            'name': lang.get('name'),
            'url': lang.get('url'),
            'active': lang['key'].lower() in matched_pairs
        })

    return lang_list


# helpers
def _query(content_type, attrs=None, term=None, tag=None):
    QUERYABLE_FIELD_KEYS = current_app.db.Document.QUERYABLE_FIELD_KEYS
    RESERVED_SLUGS = current_app.db.Document.RESERVED_SLUGS

    files = [f for f in current_app.db.Document.find(content_type)
             if f['slug'] not in RESERVED_SLUGS and f['status']]

    if isinstance(attrs, (str, dict)):
        attrs = [attrs]
    elif not isinstance(attrs, list):
        attrs = []

    for attr in attrs[:6]:  # max fields key is 6
        opposite = False
        attr_key = None
        attr_value = ''

        if isinstance(attr, str):
            attr_key = attr.lower()
        elif isinstance(attr, dict):
            opposite = bool(attr.pop('!', False) or attr.pop('not', False))
            if attr:
                attr_key = list(attr.keys())[0]
                attr_value = attr[attr_key]
            else:  # incase attr is empty after pop
                continue

        if attr_key is None:  # make sure has attr_key
            continue

        if attr_key not in QUERYABLE_FIELD_KEYS and '.' not in attr_key:
            attr_key = 'meta.{}'.format(attr_key)
        files = [f for f in files
                 if match_cond(f, attr_key, attr_value, opposite)]

    if term:
        files = [file for file in files if term in file['terms']]

    if tag:
        files = [file for file in files if tag in file['_tags']]

    return files


def _sorting(files, sort):
    SORTABLE_FIELD_KEYS = current_app.db.Document.SORTABLE_FIELD_KEYS

    sorts = [('priority', 1)]
    if isinstance(sort, tuple):
        sort_key = sort[0]
        if sort_key in SORTABLE_FIELD_KEYS:
            sorts.append(sort)

    sorting = []
    for f in files:
        new_entry = {'_id': f['_id']}
        for sort in sorts:
            new_entry[sort[0]] = f[sort[0]]
        sorting.append(new_entry)

    return sortedby(sorting, sorts)
