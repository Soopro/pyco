# coding=utf-8
from __future__ import absolute_import


def register_blueprints(app):
    # register regular
    from .regular import blueprint as regular_module
    app.register_blueprint(regular_module)

    # restapi
    from .restapi import blueprint as restapi_module
    app.register_blueprint(restapi_module, url_prefix='/restapi/app')

    # uploads
    from .uploads import blueprint as uploads_module
    uploads_prefix = '/{}'.format(app.config.get('UPLOADS_DIR'))
    app.register_blueprint(uploads_module, url_prefix=uploads_prefix)
