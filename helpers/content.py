# coding=utf-8
from __future__ import absolute_import

from flask import current_app, Markup, g

import re

from utils.validators import url_validator
from utils.misc import parse_int, match_cond, sortedby, parse_sortby


def query_by_files(content_type=None, attrs=None, term=None,
                   offset=0, limit=1, sortby=None):
    # query
    files = _query(files=g.files,
                   content_type=content_type,
                   attrs=attrs,
                   term=term)

    total_count = len(files)

    # sorting
    sorting = _sorting(files, parse_sortby(sortby))

    limit = parse_int(limit, 1, True)
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
    tmpls = [tmpl.replace('^', '') for tmpl in _config.get('templates', [])
             if tmpl.startswith('^')]

    if parent_slug == current_app.config.get('DEFAULT_INDEX_SLUG'):
        parent_slugs = ['', parent_slug]
    else:
        parent_slugs = [parent_slug]

    if tmpls:
        segments = [f for f in g.files if f['template'] in tmpls and
                    f['parent'] in parent_slugs and
                    f['content_type'] == type_slug]
        segments = sortedby(segments, [('priority', 1), sortby])[:60]
    else:
        segments = []
    return segments


# search
def search_by_files(keywords, content_type=None,
                    offset=0, limit=0, use_tags=True):
    if content_type:
        files = [f for f in g.files if f['content_type'] == content_type]
    else:
        files = g.files

    if not keywords:
        results = files
    else:
        results = []
        if isinstance(keywords, basestring):
            keywords = keywords.split()
        elif not isinstance(keywords, list):
            keywords = []

        def _search_match(keyword, f):
            if keyword in f['tags'] and keyword in f['participle']:
                return True
            return False

        results = files
        for kw in keywords:
            results = [f for f in results if _search_match(kw, f)]

    limit = parse_int(limit, 1, True)
    offset = parse_int(offset, 0, 0)

    return results[offset:offset + limit], len(results)


def find_content_file_by_id(file_id):
    if not file_id:
        return None
    for f in g.files:
        if f['_id'] == file_id:
            return f
    return None


def find_content_file(type_slug, file_slug):
    if not type_slug:
        type_slug = 'page'
    for f in g.files:
        if f['slug'] == file_slug and f['content_type'] == type_slug:
            return f
    return None


def parse_page_content(content_string):
    return Markup(content_string)


def parse_page_metas(page, current_id=None):
    data = dict()
    meta = page.get('meta')
    for m in meta:
        data[m] = meta[m]
    data['id'] = unicode(page['_id'])
    data['app_id'] = unicode(page['app_id'])
    data['slug'] = page['slug']
    data['type'] = data['content_type'] = page['content_type']
    data['template'] = page['template']
    data['parent'] = page['parent']
    data['priority'] = page['priority']
    data['status'] = page['status']
    data['date'] = page['date']
    data['value'] = page['value']
    data['tags'] = page['tags']
    data['terms'] = page['terms']
    data['price'] = page['price']
    data['updated'] = page['updated']
    data['creation'] = page['creation']
    data['excerpt'] = gen_file_excerpt(page['content'])
    data['description'] = meta.get('description') or data['excerpt']
    data['url'] = gen_page_url(page)
    data['path'] = gen_page_path(page)

    # content marks
    config = current_app.config
    if data['slug'] == config.get('DEFAULT_INDEX_SLUG'):
        data['is_front'] = True
    if data['slug'] == config.get('DEFAULT_404_SLUG'):
        data['is_404'] = True
    if unicode(data['id']) == unicode(current_id):
        data['is_current'] = True

    return data


def gen_file_excerpt(content, excerpt_length=144):
    excerpt_ellipsis = u'&hellip;'
    excerpt = re.sub(r'<.*?>', '', content).strip()
    return u'{}{}'.format(excerpt[0:excerpt_length], excerpt_ellipsis)


def gen_page_path(data, static_type='page', index='index'):
    slug = data.get('slug')
    if data['content_type'] == static_type:
        if slug == index:
            slug = ''
        path = u'/{}'.format(slug)
    else:
        path = u'/{}/{}'.format(data['content_type'], slug)
    return path


def gen_page_url(data, static_type='page', index='index'):
    slug = data.get('slug')
    if data.get('content_type') == static_type:
        if slug == index:
            slug = ''
        url = u'{}/{}'.format(g.curr_base_url, slug)
    else:
        url = u'{}/{}/{}'.format(g.curr_base_url, data['content_type'], slug)
    return url


# menus
def helper_wrap_menu(app, base_url=u''):
    if not app['menus']:
        return {}

    def process_menu_url(menu):
        for item in menu:
            link = item.get('link', '')
            if link:
                # url
                if url_validator(link):
                    item['url'] = link
                else:
                    item['url'] = u'{}/{}'.format(base_url, link.strip('/'))
                # path
                if url_validator(link):
                    if link.startswith(base_url):
                        _path = link.replace(base_url, '')
                        item['path'] = u'/{}'.format(_path)
                    else:
                        item['path'] = u''
                elif not link.startswith('/'):
                    item['path'] = u'/{}'.format(link)
                else:
                    item['path'] = link
                # hash
                if not url_validator(link):
                    _relpath = link.strip('/')
                    _hashtag = '' if _relpath.startswith('#') else '#'
                    item['hash'] = u'{}{}'.format(_hashtag, _relpath)
                else:
                    item['hash'] = u''
            else:
                item['url'] = u''
                item['hash'] = u''
                item['path'] = u''

            # name
            item['name'] = item['name'] or item['key']

            # nodes
            item['nodes'] = process_menu_url(item.get('nodes', []))
        return menu

    menu_dict = {}
    for slug, nodes in app['menus'].iteritems():
        nodes = process_menu_url(nodes)
        menu_dict[slug] = nodes
    return menu_dict


# category
def helper_wrap_category(app, included_term_keys=None):
    if not app['categories'] or not isinstance(app['categories'], dict):
        return None

    # `included_term_keys` could be None or some other empty data.
    # as long as this parameter is given, result terms must limited.
    if included_term_keys is False:
        included_term_keys = None  # reset to None for further usage.
    elif not isinstance(included_term_keys, list):
        included_term_keys = []

    category = app['categories']

    return {
        'name': category.get('name'),
        'content_types': category.get('content_types', []),
        'terms': _get_category_terms(category, included_term_keys),
    }


def _get_category_terms(category, included_term_keys=None, nest_output=True):
    if not category['terms'] or not isinstance(category['terms'], list):
        return []

    def __check_term(term):
        if not term.get('key') or term.get('status') == 0:
            return False
        elif isinstance(included_term_keys, list):
            return term['key'] in included_term_keys
        else:
            return True

    term_list = [{
        'key': term['key'],
        'parent': term.get('parent', u''),
        'meta': term.get('meta', {}),
    } for term in category['terms'] if __check_term(term)]

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
                'parent': u'',  # clear parent
                'meta': child['meta']
            } for child in children]
    else:
        output_terms = term_list

    return output_terms


# slot
def helper_wrap_slot(app):
    if not app['slots']:
        return {}
    slots_map = {}
    for k, v in app['slots'].iteritems():
        slots_map[k] = {
            'name': v.get('src', u''),
            'src': v.get('src', u''),
            'route': v.get('route', u''),
            'scripts': v.get('scripts', u''),
        }
    return slots_map


# languages
def helper_wrap_languages(languages, locale):
    """ languages data sample
    [
       {'key': 'zh_CN', 'name': '汉语', 'url': 'http://.....'},
       {'key': 'en_US', 'name': 'English', 'url': 'http://.....'}
    ]
    """

    if not languages or not isinstance(languages, list):
        return []

    trans_list = [trans for trans in languages if trans.get('key')]
    lang = locale.split('_')[0]

    for trans in trans_list:
        trans_key = trans['key'].lower()
        if trans_key == locale.lower() or trans_key == lang.lower():
            trans['active'] = True

    return trans_list


# helpers
def _query(files, content_type=None, attrs=None, term=None):
    QUERYABLE_FIELD_KEYS = current_app.config.get('QUERYABLE_FIELD_KEYS')
    RESERVED_SLUGS = current_app.config.get('RESERVED_SLUGS')

    if content_type:
        files = [f for f in files if f['content_type'] == content_type and
                 f['slug'] not in RESERVED_SLUGS]
    else:
        files = [f for f in files if f['slug'] not in RESERVED_SLUGS]

    if isinstance(attrs, (basestring, dict)):
        attrs = [attrs]
    elif not isinstance(attrs, list):
        attrs = []

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

        if attr_key not in QUERYABLE_FIELD_KEYS and '.' not in attr_key:
            attr_key = 'meta.{}'.format(attr_key)
        files = [f for f in files
                 if match_cond(f, attr_key, attr_value, force, opposite)]

    if term:
        output = []
        for file in files:
            if term in file['terms']:
                output.append(file)
    else:
        output = files

    return output


def _sorting(files, sort):
    SORTABLE_FIELD_KEYS = current_app.config.get('SORTABLE_FIELD_KEYS')

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
