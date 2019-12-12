# coding=utf8

from .controllers import *

urlpatterns = [
    ('/', rendering, 'GET'),
    ('/<file_slug>', rendering, 'GET'),
    ('/<content_type_slug>/<file_slug>', rendering, 'GET'),
]
