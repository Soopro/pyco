# coding=utf8

from .controllers import get_uploads

urlpatterns = [
    ('/<path:filepath>', get_uploads, 'GET')
]
