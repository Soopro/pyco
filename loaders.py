# coding=utf8

from utils.files import ensure_dirs

from types import ModuleType
import os


def load_config(app, config_name='config.py'):
    app.config.from_pyfile(config_name)
    app.config.setdefault('DEBUG', False)
    app.config.setdefault('STATIC_PATH', 'static')

    app.config.setdefault('UPLOADS_DIR', 'uploads')
    app.config.setdefault('BACKUPS_DIR', 'backups')
    app.config.setdefault('PLUGINS_DIR', 'plugins')

    app.config.setdefault('THEMES_DIR', 'themes')
    app.config.setdefault('THEME_NAME', 'default')

    app.config.setdefault('BASE_URL', '/')
    app.config.setdefault('RES_URL', '')
    app.config.setdefault('UPLOADS_URL', '')
    app.config.setdefault('THEME_URL', '')
    app.config.setdefault('API_URL', '')

    app.config.setdefault('PLUGINS', [])

    app.config.setdefault('HOST', '0.0.0.0')
    app.config.setdefault('PORT', 5500)

    app.config.setdefault('SYS_ICONS', ['favicon.ico',
                                        'apple-touch-icon-precomposed.png',
                                        'apple-touch-icon.png'])

    app.config.setdefault('IMAGE_MEDIA_EXTS',
                          ('jpg', 'jpe', 'jpeg', 'png', 'gif', 'bmp', 'tiff'))

    app.config.setdefault('ADMIN_PORT', 5510)
    app.config.setdefault('ADMIN_BASE_URL', ':5510/')

    app.debug = app.config['DEBUG']

    ensure_dirs(
        app.config['UPLOADS_DIR'],
        app.config['BACKUPS_DIR'],
        app.config['PLUGINS_DIR'],
    )


def load_plugins(app):
    plugins = app.config.get('PLUGINS')
    loaded_plugins = []
    for module_or_module_name in plugins:
        if type(module_or_module_name) is ModuleType:
            loaded_plugins.append(module_or_module_name)
        elif isinstance(module_or_module_name, str):
            try:
                module = __import__(module_or_module_name)
            except ImportError as err:
                raise err
            loaded_plugins.append(module)
    app.plugins = loaded_plugins


def load_metas(app):
    site = app.db.Site()
    theme_path = os.path.join(app.config.get('THEMES_DIR'),
                              app.config.get('THEME_NAME'))
    theme_meta = app.db.Theme(theme_path)

    return {
        '_id': site.get('app_id', 'pyco_app'),
        'slug': site.get('slug', 'pyco'),
        'type': site.get('type', 'ws'),
        'locale': site.get('locale', 'en_US'),
        'content_types': site.get('content_types', {'page': 'Pages'}),
        'categories': site.get('categories', None),
        'menus': site.get('menus', None),
        'slots': site.get('slots', None),
        'meta': site.get('meta', {}),
        'languages': site.get('languages', {}),
        'theme_meta': theme_meta
    }
