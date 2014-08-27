#coding=utf-8
from __future__ import absolute_import


DEFAULT_PAGINATION_LIMIT = 10


def request_url(_, env, ctx):
    if env.get("is_site_index") is True:
        request = env.get("request")
        try:
            current_page = max(int(request.args.get("page")), 1)
        except (ValueError, TypeError):
            current_page = 1
        ctx["pagination_current_page"] = current_page
    return


def get_pages(cfg, env, ctx):
    current_page = ctx.get("pagination_current_page")
    if current_page and isinstance(current_page, int):
        pagination_limit = cfg.get("PAGINATION_LIMIT", DEFAULT_PAGINATION_LIMIT)
        total = page_count(pagination_limit, len(env["pages"]))
        current_page = min(current_page, total)
        start = (current_page-1)*pagination_limit
        end = current_page*pagination_limit
        ctx["pages"] = env["pages"][start:end]
        ctx["pagination"] = dict()
        ctx["pagination"]["current_page"] = current_page
        ctx["pagination"]["has_prev_page"] = current_page > 1
        ctx["pagination"]["has_next_page"] = current_page < total
    return


def page_count(pagination_limit, total):
    return max((total+pagination_limit-1)/pagination_limit, 1)