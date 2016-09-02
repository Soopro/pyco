# coding=utf8
from __future__ import absolute_import

from views.base import get_content
from views.restapi import (get_view_metas,
                           search_view_contents,
                           query_view_contents,
                           query_view_sides,
                           get_view_content_list,
                           get_view_content)

urlpatterns = [
    ('/', get_content, "GET"),
    ('/<file_slug>/', get_content, "GET"),
    ('/<content_type_slug>/<file_slug>/', get_content, "GET"),

    # restapi
    ('/api/app/<app_id>/view/metas', get_view_metas, "GET"),
    ('/api/app/<app_id>/view/search', search_view_contents, "POST"),
    ('/api/app/<app_id>/view/query', query_view_contents, "POST"),
    ('/api/app/<app_id>/view/query_sides', query_view_sides, "POST"),
    ('/api/app/<app_id>/view/content',
        get_view_content_list, "GET"),
    ('/api/app/<app_id>/view/content/<type_slug>',
        get_view_content_list, "GET")
    ('/api/app/<app_id>/view/content/<type_slug>/<file_slug>',
        get_view_content, "GET")
]
