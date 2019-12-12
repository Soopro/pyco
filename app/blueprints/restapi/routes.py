# coding=utf8

from .controllers import *

urlpatterns = [
    # contents
    ('/<app_id>/view/metas', get_view_metas, 'GET'),
    ('/<app_id>/view/segments', get_view_segments, 'GET'),
    ('/<app_id>/view/category', get_view_category, 'GET'),
    ('/<app_id>/view/content/<type_slug>', get_view_content_list, 'GET'),
    ('/<app_id>/view/content/<type_slug>/<slug>', get_view_content, 'GET'),
    ('/<app_id>/view/search', search_view_contents, 'POST'),
    ('/<app_id>/view/query', query_view_contents, 'POST'),
]
