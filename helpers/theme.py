# coding=utf-8
from __future__ import absolute_import

from flask import current_app
import os


def theme_name():
    return current_app.config.get("THEME_NAME")


def get_theme_path(tmpl_name):
    return "{}{}".format(tmpl_name,
                         current_app.config.get('TEMPLATE_FILE_EXT'))


def get_theme_abs_path(tmpl_path):
    return os.path.join(current_app.root_path,
                        current_app.template_folder,
                        tmpl_path)
