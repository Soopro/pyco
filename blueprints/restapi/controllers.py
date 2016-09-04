# coding=utf-8
from __future__ import absolute_import

from helpers.common import *

from utils.request import get_param, get_args
from utils.response import output_json

from helpers.app import helper_record_statistic, helper_get_statistic
from helpers.content import (read_page_metas,
                             helper_render_ext_slots,
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

    site_meta = curr_app["meta"]
    site_meta['title'] = curr_app["title"]
    site_meta['description'] = curr_app["description"]
    site_meta['slug'] = curr_app['slug']
    site_meta["id"] = curr_app["_id"]
    site_meta["type"] = curr_app['type']

    translates = curr_app['translates']
    locale = curr_app['locale']

    ext_slots = curr_app["slots"]
    for k, v in ext_slots.iteritems():
        ext_slots[k] = helper_render_ext_slots(v, curr_app)

    context = {
        "app_id": curr_app["_id"],
        "site_meta": site_meta,
        "theme_meta": theme_meta,
        "base_url": g.curr_base_url,
        "theme_url": config.get("THEME_URL", u''),
        "libs_url": config.get("LIBS_URL", u''),
        "lang": locale.split('_')[0],
        "locale": locale,
        "translates": helper_wrap_translates(translates, locale),
        "socials": helper_wrap_socials(curr_app['socials']),
        "menu": helper_wrap_menu(curr_app['menus'], base_url),
        "taxonomy": helper_wrap_taxonomy(curr_app['taxonomies']),
        "content_types": curr_app['content_types'],
        "slot": ext_slots
    }
    return context


@output_json
def search_view_contents(app_id):
    pass


@output_json
def query_view_contents(app_id):
    pass


@output_json
def query_view_sides(app_id):
    pass


@output_json
def get_view_content_list(app_id, type_slug=None):
    perpage = get_args('perpage', default=0)
    paged = get_args('paged', default=0)
    sortby = get_args('sortby', default='', multiple=True)
    with_content = get_args('with_content', default=False)
    priority = get_args('priority', default=True)

    with_content = bool(with_content)
    priority = bool(priority)

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

    perpage = parse_int(perpage, 12, True)
    paged = parse_int(paged, 1, True)

    if with_content:
        # max 24 is returned while use with_content
        perpage = min(perpage, 24)

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
        p_content = p.pop('content', u'')
        p = read_page_metas(p, theme_opts)
        if with_content:
            p['content'] = parse_content(p_content)
        run_hook("get_page_data", data=p)
        pages.append(p)
    run_hook("get_pages", pages=pages, current_page_id=None)

    for p in pages:
        _add_pagination(p, curr_index, total_count, paged, max_pages)
        curr_index += 1

    return pages


@output_json
def get_view_content(app_id, type_slug, file_slug):
    content_file = find_content_file(type_slug, file_slug)
    if not content_file:
        Exception('content file not found.')
    theme_opts = curr_app['theme_meta'].get('options', {})

    page_content = {'content': content_file.pop('content', u'')}
    run_hook("before_parse_content", content=page_content)
    page_content['content'] = parse_content(page_content['content'])
    run_hook("after_parse_content", content=page_content)

    run_hook("before_read_page_meta", headers=content_file)
    page_meta = read_page_metas(content, theme_opts)
    run_hook("after_read_page_meta", meta=page_meta)

    return output(page_meta, page_content['content'])


# helpers
def _add_pagination(content, index, total_count, paged, max_pages):
    content['pagination'] = {
        'num': index + 1,
        'index': index,
        'paged': paged,
        'total_pages': max_pages,
        'total_count': total_count,
        'has_more': total_count - 1 > index,
    }
    return content


# outputs
def output(content_file, content_body=None):
    if content_body:
        content_file["content"] = content_body
    return content_file
