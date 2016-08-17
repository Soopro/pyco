# coding=utf-8
from __future__ import absolute_import

from flask import current_app, request, abort, render_template, redirect, g
import os

from utils.response import make_content_response

from helpers.common import (run_hook,
                            get_app_metas,
                            make_redirect_url,
                            make_dotted_dict)
from helpers.content import (content_not_found_full_path,
                             content_splitter,
                             init_context,
                             get_file_path,
                             get_pages,
                             parse_page_meta,
                             parse_file_metas,
                             parse_content)
from helpers.theme import get_theme_path, get_theme_abs_path


def get_content(file_slug='index', content_type_slug='page'):
    # load
    get_app_metas()
    run_hook("config_loaded", config=current_app.config)

    config = current_app.config
    view_ctx = init_context()
    status_code = 200
    is_not_found = False

    # for pass intor hook
    file = {"path": None}
    file_content = {"content": None}

    base_url = config.get("BASE_URL")
    charset = config.get('CHARSET')

    redirect_to = {"url": None}
    run_hook("request_url", request=request)

    file["path"] = get_file_path(file_slug, content_type_slug)
    # hook before load content
    run_hook("before_load_content", file=file)
    # if not found
    if file["path"] is None:
        is_not_found = True
        status_code = 404
        file["path"] = content_not_found_full_path()
        if not os.path.isfile(file["path"]):
            # without not found 404 file
            abort(404)

    # read file content
    if is_not_found:
        run_hook("before_404_load_content", file=file)

    with open(file['path'], "r") as f:
        file_content['content'] = f.read().decode(charset)

    if is_not_found:
        run_hook("after_404_load_content", file=file, content=file_content)

    run_hook("after_load_content", file=file, content=file_content)

    # parse file content
    tmp_file_content = file_content["content"]
    meta_string, content_string = content_splitter(tmp_file_content)

    meta_string = {"meta": meta_string}
    run_hook("before_read_page_meta", meta_string=meta_string)
    try:
        headers = parse_page_meta(meta_string['meta'])
    except Exception as e:
        raise Exception("{}: {}".format(str(e), file["path"]))

    run_hook("after_read_page_meta", headers=headers)
    theme_opts = config['THEME_META'].get('options', {})
    page_meta = parse_file_metas(headers,
                                 file["path"],
                                 content_string,
                                 theme_opts)
    redirect_to = {"url": None}
    run_hook("single_page_meta", page_meta=page_meta, redirect_to=redirect_to)

    c_type = str(page_meta.get('type'))
    if c_type.startswith('_') and not redirect_to["url"]:
        default_404_slug = config.get("DEFAULT_404_SLUG")
        redirect_to["url"] = "{}/{}".format(base_url, default_404_slug)

    content_redirect_to = make_redirect_url(redirect_to.get("url"), base_url)
    if content_redirect_to and request.url != content_redirect_to:
        return redirect(redirect_to["url"], code=302)

    view_ctx["meta"] = page_meta

    # content
    page_content = dict()
    page_content['content'] = content_string
    run_hook("before_parse_content", content=page_content)
    page_content['content'] = parse_content(page_content['content'])
    run_hook("after_parse_content", content=page_content)
    view_ctx["content"] = page_content['content']

    # pages
    pages = get_pages()
    for page in pages:
        run_hook("get_page_data", data=page)
    run_hook("get_pages", pages=pages, current_page=page_meta)
    view_ctx["pages"] = pages

    # template
    template = dict()
    template['file'] = view_ctx["meta"].get("template")
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
