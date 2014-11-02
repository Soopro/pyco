#coding=utf-8
from __future__ import absolute_import


def generate_pagination(current_page, pagination_limit, resouce_pages):
    total = page_count(pagination_limit, len(resouce_pages))
    current_page = min(current_page, total)
    start = (current_page-1)*pagination_limit
    end = current_page*pagination_limit

    paged_pages = dict()
    paged_pages = resouce_pages[start:end]

    pagination = dict()
    pagination["current_flip_page"] = current_page
    pagination["has_prev_flip_page"] = current_page > 1
    pagination["has_next_flip_page"] = current_page < total
    return paged_pages, pagination

def page_count(pagination_limit, total):
    return max((total+pagination_limit-1)/pagination_limit, 1)