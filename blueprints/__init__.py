# coding=utf-8
from __future__ import absolute_import
from .tradition import blueprint as tradition_module


def register_blueprints(app):
    # register blueprints
    app.register_blueprint(tradition_module)
