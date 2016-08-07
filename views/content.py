# coding=utf-8
from __future__ import absolute_import

import os
from flask import current_app, request, abort, render_template, redirect
from helpers.init import *
from utils.misc import (make_content_response,
                        helper_make_dotted_dict,
                        helper_process_url)


def get_content(_):
    # init
    config = current_app.config
    status_code = 200
    is_not_found = False

    # for pass intor hook
    file = {"path": None}
    file_content = {"content": None}

    # load
    load_metas(config)
    plugins = load_plugins(config.get("PLUGINS"))
    run_hook(plugins, "plugins_loaded")

    current_app.debug = config.get("DEBUG")
    view_ctx = init_context(request, config)

    run_hook(plugins, "config_loaded", config=config)

    base_url = config.get("BASE_URL")
    charset = config.get('CHARSET')

    redirect_to = {"url": None}
    run_hook(plugins, "request_url", request=request, redirect_to=redirect_to)
    site_redirect_url = helper_process_url(redirect_to.get("url"),
                                           config.get("BASE_URL"))
    if site_redirect_url and request.url != site_redirect_url:
        return redirect(site_redirect_url, code=301)

    # redirect to index if it is restful app
    if current_app.restful and request.path.rstrip('/') != '':
        return redirect(base_url, code=301)

    file["path"] = get_file_path(config, request.path)
    # hook before load content
    run_hook(plugins, "before_load_content", file=file)
    # if not found
    if file["path"] is None:
        is_not_found = True
        status_code = 404
        file["path"] = content_not_found_full_path(config)
        if not check_file_exists(file["path"]):
            # without not found 404 file
            abort(404)

    # read file content
    if is_not_found:
        run_hook("before_404_load_content", file=file)

    with open(file['path'], "r") as f:
        file_content['content'] = f.read().decode(charset)

    if is_not_found:
        run_hook("after_404_load_content",
                 file=file,
                 content=file_content)
    run_hook(plugins, "after_load_content", file=file, content=file_content)

    # parse file content
    tmp_file_content = file_content["content"]
    meta_string, content_string = content_splitter(tmp_file_content)

    try:
        page_meta = parse_page_meta(plugins, meta_string)
    except Exception as e:
        e.current_file = file["path"]
        raise e

    page_meta = parse_file_attrs(page_meta,
                                 file["path"],
                                 content_string,
                                 config,
                                 view_ctx)

    redirect_to = {"url": None}

    run_hook(plugins, "single_page_meta",
             page_meta=page_meta,
             redirect_to=redirect_to)

    c_type = str(page_meta.get('type'))
    if c_type.startswith('_') and not redirect_to["url"]:
        default_404_slug = config.get("DEFAULT_404_SLUG")
        redirect_to["url"] = "{}/{}".format(base_url, default_404_slug)

    content_redirect_to = helper_process_url(redirect_to.get("url"),
                                             base_url)
    if content_redirect_to and request.url != content_redirect_to:
        return redirect(redirect_to["url"], code=302)

    view_ctx["meta"] = page_meta

    page_content = dict()

    page_content['content'] = content_string
    run_hook(plugins, "before_parse_content", content=page_content)

    page_content['content'] = parse_content(page_content['content'])
    run_hook(plugins, "after_parse_content", content=page_content)

    view_ctx["content"] = page_content['content']

    # content
    pages = get_pages(config, view_ctx, plugins) if not current_app.restful else []
    view_ctx["pages"] = pages

    run_hook(plugins, "get_pages",
             pages=view_ctx["pages"],
             current_page=view_ctx["meta"])
    # template
    template = dict()

    template['file'] = view_ctx["meta"].get("template")

    run_hook(plugins, "before_render", var=view_ctx, template=template)

    template_file_path = theme_path_for(config, template['file'])
    template_file_absolute_path = theme_absolute_path_for(
        template_file_path)

    if not os.path.isfile(template_file_absolute_path):
        template['file'] = None
        default_template = config.get('DEFAULT_TEMPLATE')
        template_file_path = theme_path_for(config, default_template)

    # make dotted able
    for k, v in view_ctx.iteritems():
        view_ctx[k] = helper_make_dotted_dict(v)

    output = {}
    output['content'] = render_template(template_file_path,
                                        **view_ctx)
    run_hook(plugins, "after_render", output=output)
    return make_content_response(output['content'], status_code)
