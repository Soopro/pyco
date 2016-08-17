# coding=utf-8
from __future__ import absolute_import

from helpers.common import *
from helpers.restapi import _query, _add_pagination
from utils.request import get_param, get_args
from utils.response import make_json_response


def new_content_api():
    param_fields = get_param('fields', False, [])
    param_metas = get_param('metas', False, [])
    param_sortby = get_param('sortby', False, [])
    param_limit = get_param('limit', False, 0)
    param_offset = get_param('offset', False, 0)
    param_desc = get_param('desc', False, True)
    param_priority = get_param('priority', False, True)

    # init
    config = current_app.config
    MAXIMUM_QUERY = config.get('MAXIMUM_QUERY', 60)
    plugins = g.plugins
    view_ctx = init_context()
    status_code = 200

    theme_meta_options = view_ctx["theme_meta"].get('options', {})

    # set default params
    if not param_sortby:
        param_sortby = theme_meta_options.get('sortby', 'updated')
        if isinstance(param_sortby, basestring):
            param_sortby = [param_sortby]
        elif not isinstance(param_sortby, list):
            param_sortby = []

    if not param_limit:
        param_limit = theme_meta_options.get('perpage', 12)

    # contents
    view_ctx["pages"] = get_pages(config, view_ctx, plugins)

    run_hook("get_pages",
             pages=view_ctx["pages"],
             current_page={})

    run_hook("before_render", var=view_ctx, template=None)

    # make conditions
    conditions = param_fields + param_metas

    # query from contents
    results = _query(view_ctx["pages"],
                     conditions,
                     param_sortby,
                     param_priority,
                     param_desc)
    # offset
    offset = param_offset if param_offset > 0 else 0
    # length
    length = param_limit if param_limit > 0 else MAXIMUM_QUERY
    length = max(length, MAXIMUM_QUERY)

    # resutls
    total_count = len(results)
    results = results[offset:length]
    output = {
        "results": results,
        "count": len(results),
        "total_count": total_count,
    }
    return make_json_response(output, status_code)


def get_content_api(type_slug=None):
    param_limit = get_args('limit', default=0)
    param_offset = get_args('offset', default=0)

    # init
    config = current_app.config
    MAXIMUM_QUERY = config.get('MAXIMUM_QUERY', 60)
    plugins = g.plugins
    view_ctx = view_ctx = init_context()
    status_code = 200

    # contents
    view_ctx["pages"] = get_pages(config, view_ctx, plugins)

    run_hook("get_pages", pages=view_ctx["pages"], current_page={})

    run_hook("before_render", var=view_ctx, template=None)

    # make conditions
    if type_slug:
        conditions = [{"content_type": type_slug}]

    # query from contents
    results = _query(view_ctx["pages"], conditions)

    # offset
    offset = param_offset if param_offset > 0 else 0
    # length
    length = param_limit if param_limit > 0 else MAXIMUM_QUERY
    length = max(length, MAXIMUM_QUERY)

    # results
    total_count = len(results)
    curr_index = offset
    output = []
    for f in results[offset:length]:
        output.append(_add_pagination(f, curr_index, total_count))
        curr_index += 1
    return make_json_response(output, status_code)
