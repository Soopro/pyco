# coding=utf8
from __future__ import absolute_import

from controllers import *

urlpatterns = [
    ('/', get_content, "GET"),
    ('/<file_slug>/', get_content, "GET"),
    ('/<content_type_slug>/<file_slug>/', get_content, "GET"),
]
