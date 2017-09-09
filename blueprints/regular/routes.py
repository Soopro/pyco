# coding=utf8
from __future__ import absolute_import

from .controllers import *

urlpatterns = [
    ('/', rendering, 'GET'),
    ('/<file_slug>', rendering, 'GET'),
    ('/<content_type_slug>/<file_slug>', rendering, 'GET'),
]
