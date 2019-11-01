# coding=utf8

from utils.misc import process_slug, gen_excerpt

from types import ModuleType
import os
import yaml
import re
import json
import markdown


def load_config(app, config_name='config.py'):
    app.config.from_pyfile(config_name)
    app.config.setdefault('DEBUG', False)
    app.config.setdefault('STATIC_PATH', 'static')

    app.config.setdefault('UPLOADS_DIR', 'uploads')
    app.config.setdefault('CONTENT_DIR', 'content')
    app.config.setdefault('CONTENT_FILE_EXT', '.md')

    app.config.setdefault('BASE_URL', '/')
    app.config.setdefault('RES_URL', '')
    app.config.setdefault('UPLOADS_URL', '')
    app.config.setdefault('THEME_URL', '')
    app.config.setdefault('API_URL', '')

    app.config.setdefault('PLUGINS', [])
    app.config.setdefault('INVISIBLE_PAGE_LIST', [])
    app.config.setdefault('THEME_NAME', 'default')
    app.config.setdefault('HOST', '0.0.0.0')
    app.config.setdefault('PORT', 5500)
    app.config.setdefault('SITE', {})
    app.config.setdefault('THEME_META', {})
    app.config.setdefault('SYS_ICONS', ['favicon.ico',
                                        'apple-touch-icon-precomposed.png',
                                        'apple-touch-icon.png'])

    app.config.setdefault('PLUGIN_DIR', 'plugins')
    app.config.setdefault('THEMES_DIR', 'themes')
    app.config.setdefault('TEMPLATE_FILE_EXT', '.html')
    app.config.setdefault('TPL_FILE_EXT', '.tpl')

    app.config.setdefault('SITE_DATA_FILE', 'site.json')
    app.config.setdefault('THEME_CONF_FILE', 'config.json')

    app.config.setdefault('DEFAULT_TEMPLATE', 'index')
    app.config.setdefault('DEFAULT_DATE_FORMAT', '%Y-%m-%d')
    app.config.setdefault('DEFAULT_EXCERPT_LENGTH', 600)

    app.config.setdefault('DEFAULT_INDEX_SLUG', 'index')
    app.config.setdefault('DEFAULT_404_SLUG', 'error-404')
    app.config.setdefault('DEFAULT_SEARCH_SLUG', 'search')
    app.config.setdefault('DEFAULT_CATEGORY_SLUG', 'category')
    app.config.setdefault('DEFAULT_TAG_SLUG', 'tag')

    app.config.setdefault('RESERVED_SLUGS',
                          ['index', 'search', 'category', 'tag'])
    app.config.setdefault('SORTABLE_FIELD_KEYS',
                          ('date', 'updated'))
    app.config.setdefault('QUERYABLE_FIELD_KEYS',
                          ('slug', 'parent', 'priority', 'template', 'tags',
                           'date', 'updated', 'creation'))

    app.config.setdefault('IMAGE_MEDIA_EXTS',
                          ('jpg', 'jpe', 'jpeg', 'png', 'gif', 'bmp', 'tiff'))

    app.config.setdefault('MAXIMUM_QUERY', 60)
    app.config.setdefault('MAXIMUM_STORAGE', 360)

    app.config.setdefault('USE_MARKDOWN', False)
    app.config.setdefault('MARKDOWN_EXTENSIONS', [])

    app.debug = app.config.get('DEBUG', True)


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


def load_single_file(app, content_type, slug):
    content_dir = app.config.get('CONTENT_DIR', 'content')
    content_ext = app.config.get('CONTENT_FILE_EXT', '.md')

    filename = '{}{}'.format(slug, content_ext)
    if content_type == app.config.get('DEFAULT_CONTENT_TYPE', 'page'):
        file_path = os.path.join(content_dir, filename)
    else:
        file_path = os.path.join(content_dir, content_type, filename)

    return _read_file(app, file_path)


def load_files(app, content_type):
    content_dir = app.config.get('CONTENT_DIR', 'content')
    content_ext = app.config.get('CONTENT_FILE_EXT', '.md')
    max_storage = app.config.get('MAXIMUM_STORAGE', 360)

    if content_type == app.config.get('DEFAULT_CONTENT_TYPE', 'page'):
        files_dir = content_dir
    else:
        files_dir = os.path.join(content_dir, content_type)

    file_paths = [os.path.join(files_dir, f) for f in os.listdir(files_dir)
                  if f.endswith(content_ext) and not f.startswith('_')]
    return [_read_file(app, f) for f in file_paths[:max_storage]]


def load_metas(app):
    theme_meta_file = os.path.join(app.config.get('THEMES_DIR'),
                                   app.config.get('THEME_NAME'),
                                   app.config.get('THEME_CONF_FILE'))
    site_file = os.path.join(app.config.get('CONTENT_DIR'),
                             app.config.get('SITE_DATA_FILE'))

    try:
        with open(theme_meta_file) as theme_data:
            theme_meta = json.load(theme_data)
    except Exception as e:
        err_msg = 'Load Theme Meta failed: {}'.format(str(e))
        raise Exception(err_msg)

    try:
        with open(site_file) as site_data:
            site_json_str = site_data.read()
            site = json.loads(_shortcode(app.config, site_json_str))
    except Exception as e:
        err_msg = 'Load Site Meta failed: {}'.format(str(e))
        raise Exception(err_msg)

    site_meta = site.get('meta', {})

    return {
        '_id': site.get('app_id', 'pyco_app'),
        'slug': site.get('slug', 'pyco'),
        'type': site.get('type', 'ws'),
        'locale': site.get('locale', 'en_US'),
        'content_types': site.get('content_types', {'page': 'Pages'}),
        'categories': site.get('categories', None),
        'menus': site.get('menus', None),
        'slots': site.get('slots', None),
        'meta': site_meta,
        'languages': site_meta.pop('languages', None),
        'theme_meta': theme_meta
    }


# helpers
def _read_file(app, file_path):
    with open(file_path, 'r') as fh:
        readed = fh.read()
    meta_string, content_string = _content_splitter(app.config, readed)
    try:
        meta = _file_headers(meta_string)
    except Exception as e:
        e.current_file = file_path
        raise e

    slug = _auto_page_slug(app.config, file_path)
    content_type = _auto_content_type(file_path)
    content = _convert_content(app.config, content_string)
    tags = [tag for tag in meta.pop('tags', []) if isinstance(tag, str)]

    return {
        '_id': _auto_id(app.config, file_path),
        '_keywords': [slug] + tags,
        'slug': slug,
        'content_type': content_type,
        'priority': meta.pop('priority', 0),
        'parent': meta.pop('parent', ''),
        'date': meta.pop('date', ''),
        'tags': [tag.strip().lower() for tag in tags],
        'terms': meta.pop('terms', []),
        'redirect': meta.pop('redirect', ''),
        'template': meta.pop('template', content_type),
        'status': meta.pop('status', 1),
        'meta': meta,
        'content': content,
        'excerpt': _convert_excerpt(app.config, content),
        'updated': _auto_file_updated(file_path),
        'creation': _auto_file_creation(file_path),
    }


def _content_splitter(config, file_content):
    file_content = _shortcode(config, file_content)
    pattern = r'(\n)*/\*(\n)*(?P<meta>(.*\n)*)\*/(?P<content>(.*(\n)?)*)'
    re_pattern = re.compile(pattern)
    m = re_pattern.match(file_content)
    if m is None:
        return '', ''
    return m.group('meta'), m.group('content')


def _convert_content(config, content_string):
    if config['USE_MARKDOWN']:
        markdown_exts = config['MARKDOWN_EXTENSIONS']
        return markdown.markdown(content_string, markdown_exts)
    else:
        return content_string


def _convert_excerpt(config, content):
    return gen_excerpt(content, config['DEFAULT_EXCERPT_LENGTH'])


def _shortcode(config, text):
    re_uploads_dir = re.compile(r'\[\%uploads\%\]', re.IGNORECASE)
    re_theme_dir = re.compile(r'\[\%theme\%\]', re.IGNORECASE)
    # uploads
    text = re.sub(re_uploads_dir, str(config['UPLOADS_URL']), text)
    # theme
    text = re.sub(re_theme_dir, str(config['THEME_URL']), text)
    return text


def _auto_file_updated(file_path):
    return int(os.path.getmtime(file_path))


def _auto_file_creation(file_path):
    return int(os.path.getctime(file_path))


def _auto_content_type(file_path, default_type='page'):
    path_parts = file_path.split('/')
    if len(path_parts) > 2:
        content_type = path_parts[1].lower()
    else:
        content_type = default_type
    return content_type


def _auto_id(config, file_path):
    content_dir = os.path.join(config.get('CONTENT_DIR'), '')
    page_id = file_path.replace(content_dir, '', 1).strip('/')
    return page_id


def _auto_page_slug(config, file_path):
    content_ext = config.get('CONTENT_FILE_EXT')
    if file_path.endswith(content_ext):
        file_path = os.path.splitext(file_path)[0]
    slug = file_path.split('/')[-1]
    return process_slug(slug)


def _file_headers(meta_string):
    def convert_data_decode(x):
        if isinstance(x, dict):
            return dict((k.lower(), convert_data_decode(v))
                        for k, v in x.items())
        elif isinstance(x, list):
            return list([convert_data_decode(i) for i in x])
        elif isinstance(x, (str, int, float, bool)) or x is None:
            return x
        else:
            try:
                x = str(x)
            except Exception as e:
                print(e)
                pass
        return x
    yaml_data = yaml.safe_load(meta_string)
    headers = convert_data_decode(yaml_data)
    return headers
