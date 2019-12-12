# coding=utf-8

import unittest
from pyco import app


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app_context = app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.app_context.pop()
