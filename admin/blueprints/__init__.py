# coding=utf-8
from __future__ import absolute_import


def register_admin_blueprints(app):

    from admin.blueprints.dashboard import blueprint as dashboard_module
    app.register_blueprint(dashboard_module)

    from admin.blueprints.content import blueprint as content_module
    app.register_blueprint(content_module, url_prefix='/content')

    from admin.blueprints.category import blueprint as category_module
    app.register_blueprint(category_module, url_prefix='/category')

    from admin.blueprints.media import blueprint as media_module
    app.register_blueprint(media_module, url_prefix='/media')

    from admin.blueprints.preference import blueprint as preference_module
    app.register_blueprint(preference_module, url_prefix='/preference')
