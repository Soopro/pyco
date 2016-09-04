# coding=utf-8
from __future__ import absolute_import

from flask import current_app, request, abort, render_template, redirect, g
import os
import math
from services.i18n import Translator
from utils.request import parse_args
from utils.response import make_content_response
from utils.misc import make_dotted_dict, parse_int, now
from helpers.app import (run_hook,
                         helper_get_statistic,
                         helper_redirect_url,
                         helper_render_ext_slots,
                         get_theme_path,
                         get_theme_abs_path)
from helpers.content import (find_content_file,
                             query_by_files,
                             count_by_files,
                             helper_wrap_socials,
                             helper_wrap_translates,
                             helper_wrap_menu,
                             helper_wrap_taxonomy,
                             read_page_metas,
                             parse_content)

from .helpers.jinja import (saltshaker,
                            glue,
                            rope,
                            straw,
                            timemachine,
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

    run_hook("config_loaded", config=config)

    # hidden content types
    if _check_theme_hidden_types(theme_meta, content_type_slug):
        redirect_url = helper_redirect_url(config.get("DEFAULT_404_SLUG"),
                                           base_url)
        return redirect(redirect_url, code=302)

    run_hook("request_url", request=request)

    view_ctx = dict()

    # load file content
    path = {"content_type": content_type_slug, "slug": file_slug}
    run_hook("before_load_content", path=path)
    content_file = find_content_file(path['content_type'], path['slug'])

    # if not found
    if content_file is None:
        status_code = 404
        path = {"slug": config.get("DEFAULT_404_SLUG")}
        run_hook("before_404_load_content", path=path)
        content_file = find_content_file(None, path['slug'])
        if not content_file:
            abort(404)  # without not found 404 file
            return

    if status_code == 404:
        run_hook("after_404_load_content", path=path, file=content_file)

    run_hook("after_load_content", path=path, file=content_file)

    # content
    page_content = {'content': content_file.pop('content', u'')}
    run_hook("before_parse_content", content=page_content)
    page_content['content'] = parse_content(page_content['content'])
    run_hook("after_parse_content", content=page_content)

    view_ctx["content"] = page_content['content']

    run_hook("before_read_page_meta", headers=content_file)
    page_meta = read_page_metas(content_file, theme_options)
    redirect_to = {"url": None}
    run_hook("after_read_page_meta", meta=page_meta, redirect=redirect_to)

    # page redirect
    if redirect_to["url"]:
        redirect_to = helper_redirect_url(redirect_to["url"], base_url)
        if redirect_to and request.url != redirect_to:
            return redirect(redirect_to["url"], code=302)

    view_ctx["meta"] = page_meta
    g.curr_page_id = page_meta['id']

    # site_meta
    site_meta = curr_app["meta"]
    site_meta['title'] = curr_app["title"]
    site_meta['description'] = curr_app["description"]
    site_meta['slug'] = curr_app['slug']
    site_meta["id"] = curr_app["_id"]
    site_meta["type"] = curr_app['type']
    site_meta["visit"] = helper_get_statistic(curr_app['_id'],
                                              content_file['_id'])
    # multi-language support
    set_multi_language(view_ctx, curr_app)

    # soical media support
    view_ctx["socials"] = helper_wrap_socials(curr_app['socials'])

    # menu
    view_ctx["menu"] = helper_wrap_menu(curr_app['menus'], base_url)

    # taxonomy
    view_ctx["taxonomy"] = helper_wrap_taxonomy(curr_app['taxonomies'])

    # extension slots
    ext_slots = curr_app["slots"]
    for k, v in ext_slots.iteritems():
        ext_slots[k] = helper_render_ext_slots(v, curr_app)
    view_ctx["slot"] = ext_slots

    # base view context
    view_ctx["app_id"] = curr_app["_id"]
    view_ctx["api_baseurl"] = config.get('API_URL', u'')
    view_ctx["site_meta"] = site_meta
    view_ctx["theme_meta"] = theme_meta
    view_ctx["theme_url"] = config.get('THEME_URL', u'')
    view_ctx["libs_url"] = config.get("LIBS_URL", u'')
    view_ctx["base_url"] = base_url

    # now for refresh cache
    view_ctx["now"] = now()

    # request
    view_ctx["request"] = {
        "remote_addr": g.request_remote_addr,
        "path": g.request_path,
        "url": g.request_url,
        "args": parse_args(),
    }
    view_ctx["args"] = view_ctx["request"]["args"]

    # query
    view_ctx["query"] = query_contents
    # view_ctx["query_sides"] = query_sides

    # get current content type
    view_ctx["content_type"] = _get_content_type(content_type_slug,
                                                 curr_app['content_types'])
    # template helpers
    view_ctx["saltshaker"] = saltshaker
    view_ctx["straw"] = straw
    view_ctx["rope"] = rope
    view_ctx["glue"] = glue
    view_ctx["timemachine"] = timemachine
    view_ctx["magnet"] = magnet

    # template
    template = dict()
    template['file'] = page_meta.get("template")
    run_hook("before_render", var=view_ctx, template=template)

    template_file_path = get_theme_path(template['file'])
    template_file_abs_path = get_theme_abs_path(template_file_path)

    if not os.path.isfile(template_file_abs_path):
        template['file'] = None
        default_template = config.get('DEFAULT_TEMPLATE')
        template_file_path = get_theme_path(default_template)

    # make dotted able
    for k, v in view_ctx.iteritems():
        view_ctx[k] = make_dotted_dict(v)

    output = {}
    output['content'] = render_template(template_file_path, **view_ctx)
    run_hook("after_render", output=output)

    return make_content_response(output['content'], status_code)


def _check_theme_hidden_types(theme_meta, curr_type):
    if curr_type == 'page':
        return False
    cfg_types = theme_meta.get('content_types', {})
    status_type = cfg_types.get(curr_type, {}).get('status', 1)
    return status_type == 0


def _get_content_type(content_type_slug, content_types):
    content_type = content_types.get(content_type_slug)
    if isinstance(content_type, dict):
        content_type = {'slug': content_type.get('slug'),
                        'title': content_type.get('title')}
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
    view_context["locale"] = locale
    view_context["lang"] = locale.split('_')[0]
    # make translates
    trans_list = helper_wrap_translates(app['translates'], locale)
    view_context["translates"] = make_dotted_dict(trans_list)


# query
def query_contents(attrs=[], paged=0, perpage=0, sortby=[],
                   priority=True, with_content=False):
    query_limit = 3
    if g.query_count >= query_limit:
        raise Exception('Query Overrun')
    else:
        g.query_count += 1

    curr_id = g.curr_page_id
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

    perpage = parse_int(perpage, 12, True)
    paged = parse_int(paged, 1, True)

    if with_content:
        # max 24 is returned while use with_content
        perpage = max(perpage, 24)

    # position
    total_count = count_by_files(attrs)
    max_pages = max(int(math.ceil(total_count / float(perpage))), 1)
    paged = min(max_pages, paged)

    limit = perpage
    offset = max(perpage * (paged - 1), 0)

    # query content files
    results = query_by_files(attrs, sortby, limit, offset, priority)
    pages = []
    for p in results:
        p_content = p.pop('content', u'')
        p = read_page_metas(p, theme_opts, curr_id)
        if with_content:
            p['content'] = parse_content(p_content)
        run_hook("get_page_data", data=p)
        pages.append(p)
    run_hook("get_pages", pages=pages, current_page_id=curr_id)
    pages = make_dotted_dict(pages)

    return {
        "contents": pages,
        "paged": paged,
        "count": len(pages),
        "total_count": total_count,
        "total_pages": max_pages,
        "_remain_queries": query_limit - g.query_count,
    }
