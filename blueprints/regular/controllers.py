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
                         helper_redirect_url,
                         helper_render_ext_slots,
                         get_theme_path)
from helpers.content import (find_content_file,
                             query_by_files,
                             query_sides_by_files,
                             query_segments,
                             count_by_files,
                             helper_wrap_socials,
                             helper_wrap_translates,
                             helper_wrap_menu,
                             helper_wrap_taxonomy,
                             read_page_metas,
                             parse_content)

from .helpers.jinja import (saltshaker,
                            glue,
                            straw,
                            magnet)


def rendering(content_type_slug='page', file_slug='index'):
    config = current_app.config
    status_code = 200

    base_url = g.curr_base_url
    curr_app = g.curr_app
    site_meta = curr_app['meta']
    theme_meta = curr_app['theme_meta']
    theme_options = theme_meta.get('options', {})

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
    page_content = {'content': content_file.pop('content', u'')}
    run_hook('before_parse_content', content=page_content)
    page_content['content'] = parse_content(page_content['content'])
    run_hook('after_parse_content', content=page_content)

    view_ctx['content'] = page_content['content']

    run_hook('before_read_page_meta', headers=content_file)
    page_meta = read_page_metas(content_file, theme_options)
    redirect_to = {'url': None}
    run_hook('after_read_page_meta', meta=page_meta, redirect=redirect_to)

    # page redirect
    if redirect_to['url']:
        redirect_to = helper_redirect_url(redirect_to['url'], base_url)
        if redirect_to and request.url != redirect_to:
            return redirect(redirect_to['url'], code=302)

    view_ctx['meta'] = page_meta
    view_ctx['content_type'] = _get_content_type(content_type_slug)
    g.curr_page_id = page_meta['id']

    # site_meta
    site_meta = curr_app['meta']
    site_meta['slug'] = curr_app['slug']
    site_meta['id'] = curr_app['_id']
    site_meta['type'] = curr_app['type']

    # multi-language support
    set_multi_language(view_ctx, curr_app)

    # soical media support
    view_ctx['socials'] = helper_wrap_socials(curr_app['socials'])

    # menu
    view_ctx['menu'] = helper_wrap_menu(curr_app['menus'], base_url)

    # taxonomy
    view_ctx['taxonomy'] = helper_wrap_taxonomy(curr_app['taxonomies'])

    # segments
    view_ctx['segments'] = load_segments(curr_app)

    # extension slots
    ext_slots = curr_app['slots']
    for k, v in ext_slots.iteritems():
        ext_slots[k] = helper_render_ext_slots(v, curr_app)
    view_ctx['slot'] = ext_slots

    # base view context
    view_ctx['app_id'] = curr_app['_id']
    view_ctx['api_baseurl'] = config.get('API_BASEURL', u'')
    view_ctx['site_meta'] = site_meta
    view_ctx['theme_meta'] = theme_meta
    view_ctx['theme_url'] = config.get('THEME_URL', u'')
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
    view_ctx['query'] = query_contents
    view_ctx['query_sides'] = query_sides

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
    sa_mod.count_page(g.curr_page_id)
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
    # make translates
    trans_list = helper_wrap_translates(app['translates'], locale)
    view_context['translates'] = make_dotted_dict(trans_list)


# query
def _query_limit(limit):
    if g.query_count > limit:
        raise Exception('Query Overrun')
    else:
        g.query_count += 1
    return limit - g.query_count


def query_contents(attrs=None, paged=0, perpage=0, sortby=None,
                   taxonomy=None, priority=True):
    remain_queries = _query_limit(3)

    curr_id = g.curr_page_id
    theme_meta = g.curr_app['theme_meta']
    theme_opts = theme_meta.get('options', {})

    # set default params
    if isinstance(attrs, basestring):
        attrs = [{'type': unicode(attrs)}]

    if not sortby:
        sortby = theme_opts.get('sortby', 'updated')

    if not perpage:
        perpage = theme_opts.get('perpage')

    perpage = parse_int(perpage, 12, True)
    paged = parse_int(paged, 1, True)
    max_perpage = current_app.config.get('MAXIMUM_QUERY', 60)

    perpage = min(perpage, max_perpage)

    # position
    total_count = count_by_files(attrs, taxonomy)
    max_pages = max(int(math.ceil(total_count / float(perpage))), 1)
    page_range = [p for p in range(1, max_pages + 1)]
    paged = min(max_pages, paged)

    limit = perpage
    offset = max(perpage * (paged - 1), 0)

    # query content files
    results = query_by_files(attrs=attrs,
                             taxonomy=taxonomy,
                             offset=offset,
                             limit=limit,
                             sortby=sortby,
                             priority=priority)
    pages = [read_page_metas(p, theme_opts, curr_id) for p in results]
    run_hook('get_pages', pages=pages, current_page_id=curr_id)
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
        '_remain_queries': remain_queries,
    }


def query_sides(pid, attrs=None, limit=0, sortby=None,
                taxonomy=None, priority=True):
    remain_queries = _query_limit(3)

    file_id = pid or g.curr_page_id
    app = g.curr_app
    theme_opts = app['theme_meta'].get('options', {})

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
    before_pages, after_pages = query_sides_by_files(pid=file_id,
                                                     attrs=attrs,
                                                     taxonomy=taxonomy,
                                                     limit=limit,
                                                     sortby=sortby,
                                                     priority=priority)
    before_pages = [read_page_metas(content_file, theme_opts)
                    for content_file in before_pages]
    after_pages = [read_page_metas(content_file, theme_opts)
                   for content_file in after_pages]

    run_hook('get_pages', pages=before_pages, current_page_id=None)
    run_hook('get_pages', pages=after_pages, current_page_id=None)

    make_dotted_dict(before_pages)
    make_dotted_dict(after_pages)

    before = before_pages[-1] if before_pages else None
    after = after_pages[0] if after_pages else None

    if current_app.debug:
        print 'sides:', limit, len(before_pages), len(after_pages)

    return {
        'before': before,
        'after': after,
        'entires_before': before_pages,
        'entires_after': after_pages,
        '_remain_queries': remain_queries,
    }


def load_segments(app):
    theme_opts = app['theme_meta'].get('options', {})
    use_segments = theme_opts.get('segments',
                                  app['theme_meta'].get('segments'))
    if not use_segments:
        return []
    # get segment contents
    results = query_segments(app, use_segments)
    pages = []
    for p in results:
        p_content = p.pop('content', u'')
        p = read_page_metas(p, theme_opts)
        p['content'] = parse_content(p_content)
        pages.append(p)

    run_hook('get_pages', pages=pages, current_page_id=None)
    return make_dotted_dict(pages)
