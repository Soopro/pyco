# coding=utf-8
from __future__ import absolute_import

from flask import current_app, g
import markdown

from utils.validators import url_validator
from utils.misc import parse_int, match_cond, sortedby, parse_sortby


def query_by_files(attrs, taxonomy=None, offset=0, limit=1,
                   sortby=None, priority=True):
    # query
    files = _query(g.files, attrs, taxonomy)

    # sorting
    sorting = _sorting(files, parse_sortby(sortby), priority)

    limit = parse_int(limit, 1, True)
    offset = parse_int(offset, 0, 0)

    if sorting:
        ids = [item['_id'] for item in sorting[offset:offset + limit]]
        order_dict = {_id: index for index, _id in enumerate(ids)}
        files = [f for f in files if f['_id'] in ids]
        files.sort(key=lambda x: order_dict[x['_id']])
    else:
        files = files[offset:offset + limit]
    return files


def count_by_files(attrs, taxonomy=None):
    return len(_query(g.files, attrs, taxonomy))


def query_sides_by_files(pid, attrs, taxonomy=None, limit=1,
                         sortby=None, priority=True):
    # query
    files = _query(g.files, attrs, taxonomy)

    # sorting
    sorting = _sorting(files, parse_sortby(sortby), priority=True)

    limit = min(parse_int(limit, 1, True), 6)

    if sorting:
        ids = [item['_id'] for item in sorting]
    else:
        ids = [f['_id'] for f in files]

    curr_idx = None
    for idx, entry in enumerate(sorting):
        if str(entry['_id']) == pid:
            curr_idx = idx
            break

    if curr_idx is not None:
        before_ids = ids[max(curr_idx - limit, 0):curr_idx]
        befores = [f for f in files if f['_id'] in before_ids]
        before_order = {_id: idx for idx, _id in enumerate(before_ids)}
        befores.sort(key=lambda x: before_order[x['_id']])

        after_ids = ids[curr_idx + 1:curr_idx + 1 + limit]
        afters = [f for f in files if f['_id'] in after_ids]
        after_order = {_id: idx for idx, _id in enumerate(after_ids)}
        afters.sort(key=lambda x: after_order[x['_id']])
    else:
        befores = []
        afters = []

    return befores, afters


# segments
def query_segments(app, limit=24):
    _config = app['theme_meta']
    _opts = _config.get('options', {})

    tmpls = [tmpl.replace('^', '') for tmpl in _config.get('templates', [])
             if tmpl.startswith('^')]
    # sort
    sortby = parse_sortby(_opts.get('sortby', 'updated'))

    # query
    segs = sortedby([f for f in g.files if f['template'] in tmpls],
                    [('priority', 1), sortby])
    # limit
    limit = min(parse_int(limit, 24, 1), 60)

    return segs[:limit]


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
            if use_tags and keyword in f['tags']:
                return True
            if keyword in f['gist']:
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


def parse_content(content_string):
    use_markdown = current_app.config.get('USE_MARKDOWN')
    if use_markdown:
        markdown_exts = current_app.config.get('MARKDOWN_EXTENSIONS', [])
        return markdown.markdown(content_string, markdown_exts)
    else:
        return content_string


def read_page_metas(page, options, current_id=None):
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
    data['taxonomy'] = page['taxonomy']
    data['tags'] = page['tags']
    data['updated'] = page['updated']
    data['creation'] = page['creation']

    excerpt_len = options.get('excerpt_length')
    ellipsis = options.get('excerpt_ellipsis')
    data['excerpt'] = gen_file_excerpt(page['excerpt'], excerpt_len, ellipsis)

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


def gen_file_excerpt(excerpt, excerpt_length, ellipsis):
    excerpt_length = parse_int(excerpt_length, 162, True)
    if isinstance(ellipsis, basestring):
        excerpt_ellipsis = ellipsis
    else:
        excerpt_ellipsis = u'&hellip;'

    if excerpt:
        excerpt = u' '.join(excerpt.split())  # remove empty strings.
        excerpt = u'{}{}'.format(excerpt[0:excerpt_length], excerpt_ellipsis)
    return excerpt


# menus
def helper_wrap_menu(menus, base_url):
    if not menus:
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
            # nodes
            item['nodes'] = process_menu_url(item.get('nodes', []))
        return menu

    menu_dict = {}
    for slug, nodes in menus.iteritems():
        nodes = process_menu_url(nodes)
        menu_dict[slug] = nodes
    return menu_dict


# socials
def helper_wrap_socials(socials):
    """ socials json sample
    {
       'facebook':{
           'name':'Facebook',
           'url':'http://....',
           'poster':'http://....',
           'script': '....'
       },
       'twitter':{
           'name':'Twitter',
           'url':'http://....',
           'poster':'http://....',
           'script': '....'
       }
    }
    """
    if not socials:
        return []

    if isinstance(socials, list):
        # directly append if is list
        social_list = [social for social in socials if social.get('key')]
    elif isinstance(socials, dict):
        # change to list if is dict
        def _make_key(k, v):
            v.update({'key': k})
            return v
        social_list = [_make_key(k, v) for k, v in socials.iteritems()]
    else:
        social_list = []

    return social_list


# taxonomy
def helper_wrap_taxonomy(taxonomies):
    if not taxonomies:
        return {}

    tax_dict = {}

    def _parse_term(term, is_parent=True):
        term.setdefault('parent', u'')
        term.setdefault('priority', 0)
        term.setdefault('status', 1)
        term.setdefault('meta', {})
        term['meta'].setdefault('name', u'...')
        term['meta'].setdefault('figure', u'')
        if is_parent:
            term.setdefault('nodes', [])
            term['nodes'] = [_parse_term(child, False)
                             for child in term['nodes']
                             if child.get('key')]
        return term

    for slug, tax in taxonomies.iteritems():
        tax_dict[slug] = {
            'title': tax.get('title'),
            'content_types': tax.get('content_types', []),
            'terms': [_parse_term(term) for term in tax['terms']
                      if term.get('key')]
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
            v.update({'key': k})
            return v
        trans_list = [_make_key(k, v) for k, v in translates.iteritems()]

    for trans in trans_list:
        trans_key = trans['key'].lower()
        if trans_key == locale.lower() or trans_key == lang.lower():
            trans['active'] = True

    return trans_list


# helpers
def _query(files, attrs, taxonomy=None):
    FIELD_KEY_ALIASES = current_app.config.get('FIELD_KEY_ALIASES')
    QUERYABLE_FIELD_KEYS = current_app.config.get('QUERYABLE_FIELD_KEYS')
    RESERVED_SLUGS = current_app.config.get('RESERVED_SLUGS')

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

        attr_key = FIELD_KEY_ALIASES.get(attr_key, attr_key)
        if attr_key not in QUERYABLE_FIELD_KEYS and '.' not in attr_key:
            attr_key = 'meta.{}'.format(attr_key)
        files = [f for f in files
                 if f['slug'] not in RESERVED_SLUGS and
                 match_cond(f, attr_key, attr_value, force, opposite)]

    if taxonomy:
        tax_slug = taxonomy.get('tax')
        term_key = taxonomy.get('term')
        output = []

        def __match_tex_file(file):
            for item in file['taxonomy']:
                if item['tax'] == tax_slug and item['term'] == term_key:
                    return file
            return None

        for file in files:
            _f = __match_tex_file(file)
            if _f:
                output.append(_f)
    else:
        output = files

    return output


def _sorting(files, sort, priority=True):
    SORTABLE_FIELD_KEYS = current_app.config.get('SORTABLE_FIELD_KEYS')

    sorts = []
    if priority:
        sorts.append(('priority', 1))
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
