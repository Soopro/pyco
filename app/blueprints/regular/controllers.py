# coding=utf-8

from flask import current_app, request, abort, render_template, redirect, g
import os
import math

from core.services.i18n import Translator
from core.utils.request import parse_args
from core.utils.response import make_content_response
from core.utils.model import make_dotted_dict
from core.utils.misc import parse_int
from core.act.app import (run_hook,
                          get_redirect_url,
                          get_theme_path)
from core.act.content import (find_content_file,
                              find_404_content_file,
                              query_by_files,
                              query_segments,
                              gen_wrap_languages,
                              gen_wrap_category,
                              gen_wrap_menu,
                              gen_wrap_slot,
                              parse_page_metas,
                              parse_page_content)

from .helpers.jinja import (saltshaker,
                            glue,
                            straw,
                            magnet,
                            stapler)


def rendering(content_type_slug, file_slug):
    run_hook('request_url', request=request)

    config = current_app.config
    status_code = 200

    g.curr_content_type = content_type_slug
    g.curr_file_slug = file_slug

    curr_app = g.curr_app

    config['site_meta'] = curr_app['site_meta']
    config['theme_meta'] = curr_app['theme_meta']

    run_hook('config_loaded', config=make_dotted_dict(config))

    site_meta = curr_app['site_meta']
    theme_meta = curr_app['theme_meta']

    # hidden content types
    if _check_theme_hidden_types(theme_meta, content_type_slug):
        content_type_slug = None

    view_ctx = dict()

    # load file content
    path = {'content_type': content_type_slug, 'slug': file_slug}
    content_file = find_content_file(path['content_type'], path['slug'])

    # if not found
    if content_file is None:
        status_code = 404
        path = None
        content_file = find_404_content_file()

    # content
    page_content = {'content': content_file.get('content', '')}
    page_content['content'] = parse_page_content(page_content['content'])
    run_hook('get_page_content', pack=page_content)

    view_ctx['content'] = page_content['content']

    page_meta = parse_page_metas(content_file)
    redirect_to = {'url': content_file.get('redirect')}
    run_hook('get_page_meta', meta=page_meta, redirect=redirect_to)

    # page redirect
    if redirect_to['url']:
        redirect_to_url = get_redirect_url(redirect_to['url'], g.base_url)
        if redirect_to_url and request.url != redirect_to_url:
            return redirect(redirect_to_url, code=302)

    view_ctx['meta'] = page_meta
    view_ctx['content_type'] = _get_content_type(content_type_slug)
    g.curr_file_id = page_meta['id']

    # site_meta
    site_meta['slug'] = curr_app['slug']
    site_meta['id'] = curr_app['_id']
    site_meta['type'] = curr_app['type']

    # multi-language support
    set_multi_language(view_ctx, curr_app)

    # menu
    view_ctx['menu'] = gen_wrap_menu(curr_app, g.base_url)

    # slots
    view_ctx['slot'] = gen_wrap_slot(curr_app)

    # base view context
    view_ctx['app_id'] = curr_app['_id']
    view_ctx['site_meta'] = site_meta
    view_ctx['theme_meta'] = theme_meta
    view_ctx['api_url'] = g.api_url
    view_ctx['theme_url'] = g.theme_url
    view_ctx['res_url'] = g.res_url
    view_ctx['base_url'] = g.base_url

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
    view_ctx['stapler'] = stapler

    # template
    template = {'name': page_meta.get('template')}
    run_hook('before_render', context=view_ctx, template=template)

    template_file_path = get_theme_path(template['name'])

    # make dotted able
    for k, v in view_ctx.items():
        view_ctx[k] = make_dotted_dict(v)
    try:
        rendered = {
            'output': render_template(template_file_path, **view_ctx)
        }
    except Exception as e:
        if status_code == 404:
            abort(404)
        else:
            raise e
    run_hook('after_render', rendered=rendered)

    return make_content_response(rendered['output'], status_code)


def _check_theme_hidden_types(theme_meta, curr_type):
    supported_types = theme_meta.get('content_types', {})
    return bool(supported_types.get(curr_type, {}).get('cloaked'))


def _get_content_type(content_type_slug):
    c_type = g.curr_app.get('content_types', {}).get(content_type_slug)
    if isinstance(c_type, dict):
        content_type = {'slug': c_type.get('slug'),
                        'title': c_type.get('title')}
    else:
        content_type = {'slug': None, 'title': None}
    return content_type


def set_multi_language(view_context, app, lang_dir='languages'):
    locale = app['locale']
    # make i18n support
    lang_path = os.path.join(current_app.template_folder, lang_dir)
    translator = Translator(locale, lang_path)
    view_context['_'] = translator.gettext
    view_context['_t'] = translator.t_gettext
    view_context['locale'] = locale
    view_context['lang'] = locale.split('_')[0]
    # make language swither
    languages = gen_wrap_languages(app['languages'], locale)
    view_context['languages'] = make_dotted_dict(languages)


# query
def _check_query_limit(key, limit):
    if key not in g.query_map:
        g.query_map[key] = 0
    if g.query_map[key] >= limit:
        raise Exception('Query Overrun: {}'.format(limit))
    else:
        g.query_map[key] += 1
    return limit - g.query_map[key]


def _query_contents(content_type=None, attrs=[], term=None, tag=None,
                    paged=0, perpage=0, sortby=None, with_content=False):
    _check_query_limit('_query_contents',
                       current_app.config.get('CONTENT_QUERY_LIMIT', 3))

    curr_id = g.curr_file_id
    theme_meta = g.curr_app['theme_meta']
    theme_opts = theme_meta.get('options', {})

    # set default params
    if not content_type:
        content_type = current_app.db.Document.STATIC_TYPE

    if not sortby:
        sortby = theme_opts.get('sortby', 'updated')

    if not perpage:
        perpage = theme_opts.get('perpage')

    perpage = parse_int(perpage, 12, 1)
    paged = parse_int(paged, 1, 1)

    perpage = min(perpage, current_app.db.Document.MAXIMUM_QUERY)

    # position
    limit = perpage
    offset = max(perpage * (paged - 1), 0)

    # query content files
    results, total_count = query_by_files(content_type=content_type,
                                          attrs=attrs,
                                          term=term,
                                          tag=tag,
                                          offset=offset,
                                          limit=limit,
                                          sortby=sortby)
    pages = []
    for p in results:
        p_content = p.get('content', '')
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
    category = gen_wrap_category(g.curr_app, term_keys)
    return make_dotted_dict(category)


def _get_segments(content_type=None, parent='index'):
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
        p_content = p.get('content', '')
        p = parse_page_metas(p)
        p['content'] = parse_page_content(p_content)
        pages.append(p)

    run_hook('get_pages', pages=pages, current_page_id=None)
    return make_dotted_dict(pages)
