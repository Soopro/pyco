# coding=utf-8
from __future__ import absolute_import

from flask import current_app, request, abort, render_template, redirect, g
import os
import math
from services.i18n import Translator

from utils.request import parse_args
from utils.response import make_content_response
from utils.model import make_dotted_dict
from utils.misc import parse_int

from helpers.app import (run_hook,
                         helper_get_statistic,
                         helper_record_statistic,
                         helper_redirect_url,
                         get_theme_path)
from helpers.content import (find_content_file,
                             query_by_files,
                             query_segments,
                             helper_wrap_languages,
                             helper_wrap_category,
                             helper_wrap_menu,
                             helper_wrap_slot,
                             parse_page_metas,
                             parse_page_content)

from .helpers.jinja import (saltshaker,
                            glue,
                            straw,
                            magnet)


def rendering(content_type_slug='page', file_slug='index'):
    config = current_app.config
    status_code = 200

    g.curr_content_type = content_type_slug
    g.curr_file_slug = file_slug

    base_url = g.curr_base_url
    curr_app = g.curr_app
    site_meta = curr_app['meta']
    theme_meta = curr_app['theme_meta']

    config['site_meta'] = site_meta
    config['theme_meta'] = theme_meta

    run_hook('config_loaded', config=make_dotted_dict(config))

    # hidden content types
    if _check_theme_hidden_types(theme_meta, content_type_slug):
        redirect_url = helper_redirect_url(config.get('DEFAULT_404_SLUG'),
                                           base_url)
        return redirect(redirect_url, code=302)

    run_hook('request_url', request=request)

    view_ctx = dict()

    # load file content
    path = {'content_type': content_type_slug, 'slug': file_slug}
    run_hook('before_load_content', path=path)
    content_file = find_content_file(path['content_type'], path['slug'])

    # if not found
    if content_file is None:
        status_code = 404
        path = {'slug': config.get('DEFAULT_404_SLUG')}
        run_hook('before_404_load_content', path=path)
        content_file = find_content_file(None, path['slug'])
        if not content_file:
            abort(404)  # without not found 404 file
            return

    if status_code == 404:
        run_hook('after_404_load_content', path=path, file=content_file)

    run_hook('after_load_content', path=path, file=content_file)

    # content
    page_content = {'content': content_file.get('content', u'')}
    run_hook('before_parse_page_content', content=page_content)
    page_content['content'] = parse_page_content(page_content['content'])
    run_hook('after_parse_page_content', content=page_content)

    view_ctx['content'] = page_content['content']

    run_hook('before_read_page_meta', headers=content_file)
    page_meta = parse_page_metas(content_file)
    redirect_to = {'url': None}
    run_hook('after_read_page_meta', meta=page_meta, redirect=redirect_to)

    # page redirect
    if redirect_to['url']:
        redirect_to = helper_redirect_url(redirect_to['url'], base_url)
        if redirect_to and request.url != redirect_to:
            return redirect(redirect_to['url'], code=302)

    view_ctx['meta'] = page_meta
    view_ctx['content_type'] = _get_content_type(content_type_slug)
    g.curr_file_id = page_meta['id']

    # site_meta
    site_meta = curr_app['meta']
    site_meta['slug'] = curr_app['slug']
    site_meta['id'] = curr_app['_id']
    site_meta['type'] = curr_app['type']

    # record
    helper_record_statistic(curr_app['_id'], page_meta['id'])

    # multi-language support
    set_multi_language(view_ctx, curr_app)

    # menu
    view_ctx['menu'] = helper_wrap_menu(curr_app, base_url)

    # slots
    view_ctx['slot'] = helper_wrap_slot(curr_app)

    # base view context
    view_ctx['app_id'] = curr_app['_id']
    view_ctx['site_meta'] = site_meta
    view_ctx['theme_meta'] = theme_meta
    view_ctx['api_url'] = config.get('API_URL', u'')
    view_ctx['theme_url'] = config.get('THEME_URL', u'')
    view_ctx['lib_url'] = config.get('LIB_URL', u'')
    view_ctx['base_url'] = base_url

    # visit
    view_ctx['visit'] = helper_get_statistic(curr_app['_id'],
                                             content_file['_id'])
    # request
    view_ctx['request'] = {
        'remote_addr': g.request_remote_addr,
        'path': g.request_path,
        'url': g.request_url,
        'args': parse_args(),
    }

    # query contents
    view_ctx['query'] = _query_contents
    view_ctx['categorize'] = _get_category
    view_ctx['segments'] = _get_segments

    # helper functions
    view_ctx['saltshaker'] = saltshaker
    view_ctx['straw'] = straw
    view_ctx['glue'] = glue
    view_ctx['magnet'] = magnet

    # template
    template = {'name': page_meta.get('template')}
    run_hook('before_render', var=view_ctx, template=template)

    template_file_path = get_theme_path(template['name'])

    # make dotted able
    for k, v in view_ctx.iteritems():
        view_ctx[k] = make_dotted_dict(v)

    rendered = {
        'output': render_template(template_file_path, **view_ctx)
    }
    run_hook('after_render', rendered=rendered)

    sa_mod = current_app.sa_mod
    sa_mod.count_page(g.curr_file_id)
    sa_mod.count_app(g.request_remote_addr,
                     request.user_agent.string)

    return make_content_response(rendered['output'], status_code)


def _check_theme_hidden_types(theme_meta, curr_type):
    if curr_type == 'page':
        return False
    cfg_types = theme_meta.get('content_types', {})
    status_type = cfg_types.get(curr_type, {}).get('status', 1)
    return status_type == 0


def _get_content_type(content_type_slug):
    c_type = g.curr_app.get('content_types', {}).get(content_type_slug)
    if isinstance(c_type, dict):
        content_type = {'slug': c_type.get('slug'),
                        'title': c_type.get('title')}
    else:
        content_type = {'slug': None, 'title': None}
    return content_type


def set_multi_language(view_context, app):
    locale = app['locale']
    # make i18n support
    lang_dir = current_app.config.get('LANGUAGES_DIR', 'languages')
    lang_path = os.path.join(current_app.template_folder, lang_dir)
    translator = Translator(locale, lang_path)
    view_context['_'] = translator.gettext
    view_context['_t'] = translator.t_gettext
    view_context['locale'] = locale
    view_context['lang'] = locale.split('_')[0]
    # make language swither
    languages = helper_wrap_languages(app['languages'], locale)
    view_context['languages'] = make_dotted_dict(languages)


# query
def _check_query_limit(key, limit):
    if key not in g.query_map:
        g.query_map[key] = 0
    if g.query_map[key] >= limit:
        raise Exception('Query Overrun')
    else:
        g.query_map[key] += 1
    return limit - g.query_map[key]


def _query_contents(content_type=None, attrs=[], term=None,
                    paged=0, perpage=0, sortby=None, with_content=False):
    _check_query_limit('_query_contents', 3)

    curr_id = g.curr_file_id
    theme_meta = g.curr_app['theme_meta']
    theme_opts = theme_meta.get('options', {})

    # set default params
    if not sortby:
        sortby = theme_opts.get('sortby', 'updated')

    if not perpage:
        perpage = theme_opts.get('perpage')

    perpage = parse_int(perpage, 12, True)
    paged = parse_int(paged, 1, True)
    max_perpage = current_app.config.get('MAXIMUM_QUERY', 60)

    perpage = min(perpage, max_perpage)

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
        p = parse_page_metas(p, curr_id)
        if with_content:
            p['content'] = parse_page_content(p_content)
        pages.append(p)

    run_hook('get_pages', pages=pages, current_page_id=curr_id)

    max_pages = max(int(math.ceil(total_count / float(perpage))), 1)
    page_range = [n for n in range(1, max_pages + 1)]

    pages = make_dotted_dict(pages)

    return {
        'contents': pages,
        'perpage': perpage,
        'paged': paged,
        'total_count': total_count,
        'total_pages': max_pages,
        'page_range': page_range,
        'has_prev': paged > 1,
        'has_next': paged < max_pages,
    }


def _get_category(term_keys=False):
    _check_query_limit('_get_category', 1)
    category = helper_wrap_category(g.curr_app, term_keys)
    return make_dotted_dict(category)


def _get_segments(content_type=None, parent=None):
    _check_query_limit('_get_segments', 1)
    if not content_type:
        content_type = g.curr_content_type
    if not parent:
        parent = g.curr_file_slug
    app = g.curr_app
    # get segment contents
    results = query_segments(app, content_type, parent)
    pages = []
    for p in results:
        p_content = p.get('content', u'')
        p = parse_page_metas(p)
        p['content'] = parse_page_content(p_content)
        pages.append(p)

    run_hook('get_pages', pages=pages, current_page_id=None)
    return make_dotted_dict(pages)
