# coding=utf-8
from __future__ import absolute_import

from flask import current_app, g
import math

from utils.misc import (sortedby,
                        parse_int,
                        process_slug,
                        make_dotted_dict)
from utils.request import get_param, get_args
from utils.response import output_json

from helpers.app import (run_hook,
                         helper_record_statistic,
                         helper_get_statistic,
                         helper_render_ext_slots,
                         get_segment_contents)
from helpers.content import (read_page_metas,
                             query_by_files,
                             query_sides_by_files,
                             count_by_files,
                             search_by_files,
                             find_content_file,
                             parse_content,
                             helper_wrap_translates,
                             helper_wrap_socials,
                             helper_wrap_menu,
                             helper_wrap_taxonomy)


@output_json
def app_visit(app_id, file_id=None):
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
    site_meta['id'] = curr_app['_id']
    site_meta['type'] = curr_app['type']

    translates = curr_app['translates']
    locale = curr_app['locale']

    ext_slots = curr_app['slots']
    for k, v in ext_slots.iteritems():
        ext_slots[k] = helper_render_ext_slots(v, curr_app)

    context = {
        'app_id': curr_app['_id'],
        'site_meta': site_meta,
        'theme_meta': theme_meta,
        'base_url': g.curr_base_url,
        'theme_url': config.get('THEME_URL', u''),
        'libs_url': config.get('LIBS_URL', u''),
        'lang': locale.split('_')[0],
        'locale': locale,
        'translates': helper_wrap_translates(translates, locale),
        'socials': helper_wrap_socials(curr_app['socials']),
        'menu': helper_wrap_menu(curr_app['menus'], g.curr_base_url),
        'taxonomy': helper_wrap_taxonomy(curr_app['taxonomies']),
        'content_types': curr_app['content_types'],
        'slot': ext_slots
    }
    return context


@output_json
def get_view_tags(app_id, type_slug=None):
    limit = get_args('limit', default=60)
    limit = parse_int(limit, 60, True)

    if type_slug:
        type_slug = process_slug(type_slug)
        files = [f for f in g.files if f['content_type'] == type_slug]
    else:
        files = [f for f in g.files]

    tags = {}
    for f in files:
        for key in f['tags']:
            tags[key] = 1 if key not in tags else tags[key] + 1

    tag_list = [{'key': k, 'count': v} for k, v in tags.iteritems()]
    results = sortedby(tag_list, [('count', -1)])[:limit]

    return results


@output_json
def search_view_contents(app_id):
    keywords = get_param('keywords', list, default=[])
    content_type = get_param('content_type', unicode, default=None)
    attrs = get_param('attrs', list, default=['title'])
    use_tags = get_param('use_tags', bool, default=True)
    perpage = get_param('perpage', int, default=0)
    paged = get_param('paged', int, default=0)

    theme_opts = g.curr_app['theme_meta'].get('options', {})

    if not perpage:
        perpage = theme_opts.get('perpage')

    perpage, paged = _safe_paging(perpage, paged)

    limit = perpage
    offset = max(perpage * (paged - 1), 0)

    content_type = process_slug(content_type)
    results, total_count = search_by_files(content_type=content_type,
                                           keywords=keywords,
                                           attrs=attrs,
                                           use_tags=use_tags,
                                           limit=limit,
                                           offset=offset)

    max_pages = max(int(math.ceil(total_count / float(perpage))), 1)
    page_range = [p for p in range(1, max_pages + 1)]
    paged = min(max_pages, paged)

    pages = [read_page_metas(p, theme_opts, None) for p in results]
    run_hook('get_pages', pages=pages, current_page_id=None)

    return {
        'contents': pages,
        'perpage': perpage,
        'paged': paged,
        'count': len(results),
        'total_pages': max_pages,
        'total_count': total_count,
        'page_range': page_range,
        'has_prev': paged > 1,
        'has_next': paged < max_pages,
    }


@output_json
def query_view_contents(app_id):
    attrs = get_param('attrs', list, False, [])
    sortby = get_param('sortby', list, False, [])
    perpage = get_param('perpage', int, False, 1)
    paged = get_param('paged', int, False, 0)
    priority = get_param('priority', bool, False, True)
    with_content = get_param('with_content', bool, False, False)

    theme_meta = g.curr_app['theme_meta']
    theme_opts = theme_meta.get('options', {})

    # set default params
    if isinstance(attrs, basestring):
        attrs = [{'type': unicode(attrs)}]

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
    total_count = count_by_files(attrs)
    max_pages = max(int(math.ceil(total_count / float(perpage))), 1)
    page_range = [p for p in range(1, max_pages + 1)]
    paged = min(max_pages, paged)

    limit = perpage
    offset = max(perpage * (paged - 1), 0)

    # query content files
    results = query_by_files(attrs, sortby, limit, offset, priority)
    pages = []
    for p in results:
        p_content = p.pop('content', u'')
        p = read_page_metas(p, theme_opts, None)
        if with_content:
            p['content'] = parse_content(p_content)
        pages.append(p)
    run_hook('get_pages', pages=pages, current_page_id=None)

    return {
        'contents': pages,
        'perpage': perpage,
        'paged': paged,
        'count': len(pages),
        'total_count': total_count,
        'total_pages': max_pages,
        'page_range': page_range,
        'has_prev': paged > 1,
        'has_next': paged < max_pages
    }


@output_json
def query_view_sides(app_id):
    pid = get_param('pid', unicode, True)
    attrs = get_param('attrs', list, False, [])
    sortby = get_param('sortby', list, False, [])
    limit = get_param('perpage', int, False, 1)
    priority = get_param('priority', bool, False, True)

    theme_opts = g.curr_app['theme_meta'].get('options', {})

    # set default params
    if isinstance(attrs, basestring):
        attrs = [{'type': unicode(attrs)}]

    if not sortby:
        sortby = theme_opts.get('sortby', 'updated')
        if isinstance(sortby, basestring):
            sortby = [sortby]
        elif not isinstance(sortby, list):
            sortby = []

    limit = parse_int(limit, 1, True)

    # query side mongo
    before_pages, after_pages = query_sides_by_files(pid, attrs, sortby,
                                                     limit, priority)
    before_pages = [read_page_metas(content_file, theme_opts)
                    for content_file in before_pages]
    after_pages = [read_page_metas(content_file, theme_opts)
                   for content_file in after_pages]

    run_hook('get_pages', pages=before_pages, current_page_id=None)
    run_hook('get_pages', pages=after_pages, current_page_id=None)

    before = before_pages[-1] if before_pages else None
    after = after_pages[0] if after_pages else None

    return {
        'before': before,
        'after': after,
        'entires_before': before_pages,
        'entires_after': after_pages,
    }


@output_json
def get_view_content_list(app_id, type_slug=None):
    perpage = get_args('perpage', default=0)
    paged = get_args('paged', default=0)
    sortby = get_args('sortby', default='', multiple=True)
    priority = get_args('priority', default=True)

    priority = bool(priority)

    theme_opts = g.curr_app['theme_meta'].get('options', {})

    # get contents
    attrs = {'content_type': process_slug(type_slug)} if type_slug else None
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
    total_count = count_by_files(attrs)
    max_pages = max(int(math.ceil(total_count / float(perpage))), 1)
    paged = min(max_pages, paged)

    limit = perpage
    offset = max(perpage * (paged - 1), 0)

    # query content files
    results = query_by_files(attrs, sortby, limit, offset, priority)
    curr_index = offset

    pages = []
    for p in results:
        p.pop('content', u'')
        p = read_page_metas(p, theme_opts)
        pages.append(p)
    run_hook('get_pages', pages=pages, current_page_id=None)

    for p in pages:
        _add_cursor(p, curr_index, total_count, perpage, paged, max_pages)
        curr_index += 1

    return pages


@output_json
def get_view_content(app_id, type_slug, file_slug):
    content_file = find_content_file(type_slug, file_slug)
    if not content_file:
        Exception('content file not found.')
    app = g.curr_app
    theme_opts = app['theme_meta'].get('options', {})

    page_content = {'content': content_file.pop('content', u'')}
    run_hook('before_parse_content', content=page_content)
    page_content['content'] = parse_content(page_content['content'])
    run_hook('after_parse_content', content=page_content)

    run_hook('before_read_page_meta', headers=content_file)
    page_meta = read_page_metas(content_file, theme_opts)
    run_hook('after_read_page_meta', meta=page_meta, redirect=None)

    return output(page_meta, page_content['content'])


@output_json
def get_view_segments(app_id):
    app = g.curr_app
    theme_opts = app['theme_meta'].get('options', {})
    # get segment contents
    results = get_segment_contents(app)
    pages = []
    for p in results:
        p_content = p.pop('content', u'')
        p = read_page_metas(p, theme_opts)
        p['content'] = parse_content(p_content)
        pages.append(p)

    run_hook('get_pages', pages=pages, current_page_id=None)

    return pages


# helpers
def _add_cursor(content, index, total_count, perpage, paged, max_pages):
    content['cursor'] = {
        'num': index + 1,
        'index': index,
        'perpage': perpage,
        'paged': paged,
        'total_pages': max_pages,
        'total_count': total_count,
        'has_more': total_count - 1 > index,
    }
    return content


def _safe_paging(perpage, paged):
    max_perpage = current_app.config.get('MAXIMUM_QUERY', 60)
    perpage = parse_int(perpage, 12, True)
    paged = parse_int(paged, 1, True)
    return min(perpage, max_perpage), paged


# outputs
def output(content_file, content_body=None):
    if content_body:
        content_file['content'] = content_body
    return content_file
