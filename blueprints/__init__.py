# coding=utf-8
from __future__ import absolute_import


def register_blueprints(app):
    # register regular
    from .regular import blueprint as regular_module
    app.register_blueprint(regular_module)

    # register uploads
    from .uploads import blueprint as uploads_module
    uploads_dir = app.config.get('UPLOADS_DIR')
    uploads_prefix = "/{}".format(uploads_dir)
    app.register_blueprint(uploads_module, url_prefix=uploads_prefix)
