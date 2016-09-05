# coding=utf8
from __future__ import absolute_import

from .controllers import *

urlpatterns = [
    # analytics
    ('app/<app_id>/visit', app_visit, "PUT"),
    ('app/<app_id>/visit/<file_id>', app_visit, "PUT"),
    ('app/<app_id>/visit', app_visit_status, "GET"),
    ('app/<app_id>/visit/<file_id>', app_visit_status, "GET"),

    # contents
    ('app/<app_id>/view/metas', get_view_metas, "GET"),
    ('app/<app_id>/view/search', search_view_contents, "POST"),
    ('app/<app_id>/view/query', query_view_contents, "POST"),
    ('app/<app_id>/view/query_sides', query_view_sides, "POST"),
    ('app/<app_id>/view/content',
        get_view_content_list, "GET"),
    ('app/<app_id>/view/content/<type_slug>',
        get_view_content_list, "GET")
    ('app/<app_id>/view/content/<type_slug>/<file_slug>',
        get_view_content, "GET")
]
