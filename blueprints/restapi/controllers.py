# coding=utf-8
from __future__ import absolute_import

from flask import current_app, g
import math

from utils.response import output_json
from utils.request import get_param, get_args
from utils.model import make_dotted_dict
from utils.misc import parse_int

from helpers.app import (run_hook,
                         helper_record_statistic,
                         helper_get_statistic)
from helpers.content import (parse_page_metas,
                             query_by_files,
                             query_segments,
                             search_by_files,
                             find_content_file,
                             parse_page_content,
                             helper_wrap_languages,
                             helper_wrap_category,
                             helper_wrap_menu,
                             helper_wrap_slot)


@output_json
def app_visit(app_id, file_id=None):
    if app_id == g.curr_app['_id']:
        helper_record_statistic(app_id, file_id)
    return helper_get_statistic(app_id, file_id)


@output_json
def app_visit_status(app_id, file_id):
    return helper_get_statistic(app_id, file_id)


@output_json
def get_view_metas(app_id):
    config = current_app.config
    curr_app = g.curr_app

    theme_meta = curr_app['theme_meta']
    site_meta = curr_app['meta']

    config['site_meta'] = site_meta
    config['theme_meta'] = theme_meta

    run_hook('config_loaded', config=make_dotted_dict(config))

    site_meta['slug'] = curr_app['slug']
    site_meta['type'] = curr_app['type']

    languages = curr_app['languages']
    locale = curr_app['locale']

    context = {
        'site_meta': site_meta,
        'theme_meta': theme_meta,
        'base_url': g.curr_base_url,
        'theme_url': config.get('THEME_URL', u''),
        'lib_url': config.get('LIB_URL', u''),
        'lang': locale.split('_')[0],
        'locale': locale,
        'languages': helper_wrap_languages(languages, locale),
        'menu': helper_wrap_menu(curr_app, g.curr_base_url),
        'content_type': curr_app['content_types'],
        'slot': helper_wrap_slot(curr_app)
    }
    return context


@output_json
def get_view_category(app_id):
    term_keys = get_args('term_keys', default=False, multiple=True)
    return {
        'category': helper_wrap_category(g.curr_app, term_keys)
    }


@output_json
def get_view_tags(app_id, type_slug=None):
    pass
    # limit = get_args('limit', default=60)
    # limit = parse_int(limit, 60, True)

    # if type_slug:
    #     type_slug = process_slug(type_slug)
    #     files = [f for f in g.files if f['content_type'] == type_slug]
    # else:
    #     files = [f for f in g.files]

    # tags = {}
    # for f in files:
    #     for key in f['tags']:
    #         tags[key] = 1 if key not in tags else tags[key] + 1

    # tag_list = [{'key': k, 'count': v} for k, v in tags.iteritems()]
    # results = sortedby(tag_list, [('count', -1)])[:limit]

    # return results


@output_json
def search_view_contents(app_id):
    keywords = get_param('keywords', list, default=[])
    content_type = get_param('content_type', unicode, default=None)
    perpage = get_param('perpage', int, default=0)
    paged = get_param('paged', int, default=0)

    theme_opts = g.curr_app['theme_meta'].get('options', {})

    if not perpage:
        perpage = theme_opts.get('perpage')

    perpage, paged = _safe_paging(perpage, paged)

    limit = perpage
    offset = max(perpage * (paged - 1), 0)

    results, total_count = search_by_files(content_type=content_type,
                                           keywords=keywords,
                                           offset=offset,
                                           limit=limit)

    max_pages = max(int(math.ceil(total_count / float(perpage))), 1)
    paged = min(max_pages, paged)

    pages = [parse_page_metas(p) for p in results]
    run_hook('get_pages', pages=pages, current_page_id=None)

    return output_result(contents=pages, perpage=perpage, paged=paged,
                         total_pages=max_pages, total_count=total_count)


@output_json
def query_view_contents(app_id):
    attrs = get_param('attrs', list, False, [])
    content_type = get_param('content_type', unicode, default=u'')
    sortby = get_param('sortby', list, False, [])
    perpage = get_param('perpage', int, False, 1)
    paged = get_param('paged', int, False, 0)
    with_content = get_param('with_content', bool, default=False)
    term = get_param('term', dict)

    theme_meta = g.curr_app['theme_meta']
    theme_opts = theme_meta.get('options', {})

    # set default params
    if not sortby:
        sortby = theme_opts.get('sortby', 'updated')

    if not perpage:
        perpage = theme_opts.get('perpage')

    perpage, paged = _safe_paging(perpage, paged)

    # position
    limit = perpage
    offset = max(perpage * (paged - 1), 0)

    # query content files
    results, total_count = query_by_files(attrs=attrs,
                                          content_type=content_type,
                                          term=term,
                                          offset=offset,
                                          limit=limit,
                                          sortby=sortby)
    pages = []
    for p in results:
        p_content = p.get('content', u'')
        p = parse_page_metas(p)
        if with_content:
            p['content'] = parse_page_content(p_content)
        pages.append(p)
    run_hook('get_pages', pages=pages, current_page_id=None)

    max_pages = max(int(math.ceil(total_count / float(perpage))), 1)

    return output_result(contents=pages, perpage=perpage, paged=paged,
                         total_pages=max_pages, total_count=total_count)


@output_json
def get_view_content_list(app_id, type_slug=u'page'):
    perpage = get_args('perpage', default=0)
    paged = get_args('paged', default=0)
    sortby = get_args('sortby', default='', multiple=True)
    priority = get_args('priority', default=True)
    term = get_args('term')

    priority = bool(priority)

    theme_opts = g.curr_app['theme_meta'].get('options', {})

    # set default params
    if not sortby:
        sortby = theme_opts.get('sortby', 'updated')
        if isinstance(sortby, basestring):
            sortby = [sortby]
        elif not isinstance(sortby, list):
            sortby = []

    if not perpage:
        perpage = theme_opts.get('perpage')

    perpage, paged = _safe_paging(perpage, paged)

    # position
    limit = perpage
    offset = max(perpage * (paged - 1), 0)

    # query content files
    results, total_count = query_by_files(content_type=type_slug,
                                          term=term,
                                          offset=offset,
                                          limit=limit,
                                          sortby=sortby)
    curr_index = offset

    pages = []
    for p in results:
        p = parse_page_metas(p)
        pages.append(p)
    run_hook('get_pages', pages=pages, current_page_id=None)

    max_pages = max(int(math.ceil(total_count / float(perpage))), 1)

    for p in pages:
        _add_cursor(content=p,
                    index=curr_index,
                    perpage=perpage,
                    paged=paged,
                    total_pages=max_pages,
                    total_count=total_count)
        curr_index += 1

    return pages


@output_json
def get_view_content(app_id, type_slug, slug):
    content_file = find_content_file(type_slug, slug)
    if not content_file:
        Exception('content file not found.')

    page_content = {'content': content_file.get('content', u'')}
    run_hook('before_parse_page_content', content=page_content)
    page_content['content'] = parse_page_content(page_content['content'])
    run_hook('after_parse_page_content', content=page_content)

    run_hook('before_read_page_meta', headers=content_file)
    page_meta = parse_page_metas(content_file)
    run_hook('after_read_page_meta', meta=page_meta, redirect=None)

    output = page_meta
    output['content'] = page_content['content']
    return output


@output_json
def get_view_segments(app_id):
    content_type = get_args('content_type', default='page')
    parent = get_args('parent', default='index')

    app = g.curr_app

    results = query_segments(app, content_type, parent)
    pages = []
    for p in results:
        p_content = p.get('content', u'')
        p = parse_page_metas(p)
        p['content'] = parse_page_content(p_content)
        pages.append(p)

    run_hook('get_pages', pages=pages, current_page_id=None)

    return pages


# helpers
def _add_cursor(content, index, perpage, paged, total_pages, total_count):
    content['cursor'] = {
        'num': index + 1,
        'index': index,
        'perpage': perpage,
        'paged': paged,
        'page_range': [p for p in xrange(1, total_pages + 1)],
        'total_pages': total_pages,
        'total_count': total_count,
        'has_prev': paged > 1,
        'has_next': paged < total_pages,
    }
    return content


def _safe_paging(perpage, paged):
    max_perpage = current_app.config.get('MAXIMUM_QUERY', 60)
    perpage = parse_int(perpage, 12, True)
    paged = parse_int(paged, 1, True)
    return min(perpage, max_perpage), paged


# outputs
def output_result(contents, perpage, paged, total_pages, total_count):
    return {
        'contents': contents,
        'perpage': perpage,
        'paged': paged,
        'total_pages': total_pages,
        'total_count': total_count,
        'page_range': [p for p in xrange(1, total_pages + 1)],
        'has_prev': paged > 1,
        'has_next': paged < total_pages,
    }
