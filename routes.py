# coding=utf8

from __future__ import absolute_import
from views.uploads import upload
from views.restapi import get_content_api, new_content_api
from views.content import get_content
from config import UPLOADS_DIR

urlpatterns = [
    ('/', get_content, "GET"),
    ('/<file_slug>/', get_content, "GET"),
    ('/<content_type_slug>/<file_slug>/', get_content, "GET"),
    # rest api
    ('/restapi/context', get_content, "GET"),
    ('/restapi/contents',new_content_api, "GET"),
    ('/restapi/contents/<type_slug>', get_content_api, "GET"),
    ("/{}/<path:filepath>".format(UPLOADS_DIR), upload, "GET")
]