# coding=utf8
from __future__ import absolute_import

from .controllers import get_uploads

urlpatterns = [
    ('/<path:filepath>', get_uploads, 'GET')
]
