# coding=utf8
from __future__ import absolute_import

from .controllers import *

urlpatterns = [
    ('/', rendering, 'GET'),
    ('/<path:filepath>', rendering, 'GET'),
]
