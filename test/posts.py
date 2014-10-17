#coding=utf-8
from __future__ import absolute_import

from .base import BaseTest


class PostsTest(BaseTest):
    def index_test(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        return

    def index2_test(self):
        response = self.client.get("/index")
        self.assertEqual(response.status_code, 404)
        return

    def hello_test(self):
        response = self.client.get("/hello")
        self.assertEqual(response.status_code, 200)
        return

