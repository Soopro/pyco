# coding=utf-8
from __future__ import absolute_import

from views.restapi import get_content_api, new_content_api
from views.base import get_content

view_get_content = get_content
view_get_content_api = get_content_api
view_new_content_api = new_content_api
