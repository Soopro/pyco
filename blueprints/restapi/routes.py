# coding=utf8
from __future__ import absolute_import

from .controllers import *

urlpatterns = [
    # analytics
    ('/<app_id>/visit', app_visit, 'PUT'),
    ('/<app_id>/visit/<file_id>', app_visit, 'PUT'),
    ('/<app_id>/visit', app_visit_status, 'GET'),
    ('/<app_id>/visit/<file_id>', app_visit_status, 'GET'),

    # contents
    ('/<app_id>/view/metas', get_view_metas, 'GET'),
    ('/<app_id>/view/content/<type_slug>', get_view_content_list, 'GET'),
    ('/<app_id>/view/content/<type_slug>/<file_slug>',
        get_view_content, 'GET'),
    ('/<app_id>/view/tags', get_view_tags, 'GET'),
    ('/<app_id>/view/taxonomy', get_view_taxonomy, 'GET'),
    ('/<app_id>/view/segments', get_view_segments, 'GET'),
    ('/<app_id>/view/search', search_view_contents, 'POST'),
    ('/<app_id>/view/query', query_view_contents, 'POST'),
    ('/<app_id>/view/query_sides', query_view_sides, 'POST'),
]
