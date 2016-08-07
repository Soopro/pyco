# coding=utf8
import os

from flask import current_app


def theme_name(config):
    return config.get("THEME_NAME")


def theme_path_for(config, tmpl_name):
    return "{}{}".format(tmpl_name, config.get('TEMPLATE_FILE_EXT'))


def theme_absolute_path_for(tmpl_path):
    return os.path.join(current_app.root_path,
                        current_app.template_folder,
                        tmpl_path)