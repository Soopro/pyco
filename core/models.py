# coding=utf8

import os
import re
import yaml
import json
import urllib

from .utils.misc import (process_slug,
                         parse_int,
                         slug_uuid_suffix,
                         gen_excerpt,
                         guess_mimetype,
                         split_file_ext,
                         split_file_type,
                         get_from_dict)


class DBConnection:
    models = dict()
    pretreat_method = None
    data_dir = None

    def __init__(self, data_dir=None, pretreat_method=None):
        if isinstance(data_dir, str) and data_dir:
            self.data_dir = data_dir
        if callable(pretreat_method):
            self.pretreat_method = pretreat_method

    def register(self, models):
        for model in models:
            model.__pretreat_method__ = self.pretreat_method
            model.__data_dir__ = self.data_dir
            self.models[model.__name__] = model

    def __getattr__(self, name):
        try:
            attr = self.models[name]
        except Exception:
            raise Exception('Model `{}` not registerd.'.format(name))
        return attr


# base
class FlatFile:
    _id = None
    path = str()
    data = dict()
    raw = None

    __data_dir__ = None
    __pretreat_method__ = None

    def __init__(self, path):
        if path:
            self._id = self.path = path
            self.raw = self._load()

    def __getitem__(self, key):
        if key == '_id':
            return self._id
        else:
            return self.data[key]

    def __setitem__(self, key, value):
        if key == '_id':
            self._id = value
        else:
            self.data[key] = value

    def get(self, key, default=None):
        return self.data.get(key, default)

    def save(self):
        with open(self.path, 'w') as f:
            f.write(self.raw or '')
        return self._id

    def delete(self):
        if os.path.isfile(self.path):
            os.remove(self.path)
        return self._id

    def _load(self):
        if os.path.isfile(self.path):
            with open(self.path, 'r') as fh:
                readed = fh.read()
        else:
            readed = ''
        if callable(self.__pretreat_method__) and readed:
            readed = self.__pretreat_method__(readed)
        return readed

    def _prepare_field(self, x):
        if isinstance(x, dict):
            return {k.capitalize(): self._prepare_field(v)
                    for k, v in x.items()}
        elif isinstance(x, list):
            return list([self._prepare_field(i) for i in x])
        elif isinstance(x, str):
            return urllib.parse.unquote(x)
        elif isinstance(x, (int, float, bool)) or x is None:
            return x
        else:
            try:
                x = urllib.parse.unquote(str(x))
            except Exception as e:
                x = str(e)
        return x

    def _parse_field(self, x):
        if isinstance(x, dict):
            return dict((k.lower(), self._parse_field(v))
                        for k, v in x.items())
        elif isinstance(x, list):
            return list([self._parse_field(i) for i in x])
        elif isinstance(x, (str, int, float, bool)) or x is None:
            return x
        else:
            try:
                x = str(x)
            except Exception as e:
                x = str(e)
        return x

    def _abs_path(self, path):
        if self.__data_dir__:
            return os.path.join(self.__data_dir__, path)
        else:
            return path


class Configure(FlatFile):

    conf_path = 'configure.yaml'
    data = {
        'passcode_hash': '',
        'locale': 'en_US',
        'login_extra': '',
        'acc_mode': 0,
        'acc_url': '',
    }
    LOCALES = [
        {'key': 'en_US', 'name': 'English'},
        {'key': 'zh_CN', 'name': '简体中文'},
    ]

    def __init__(self):
        self.path = self._abs_path(self.conf_path)
        super(Configure, self).__init__(self.path)
        if self.raw:
            fields = yaml.safe_load(self.raw)
            self.update(self._parse_field(fields))

    def save(self):
        self.raw = yaml.safe_dump(self._prepare_field(self.data),
                                  stream=None,
                                  default_flow_style=False,
                                  indent=2,
                                  encoding=None,
                                  allow_unicode=True)
        return super(Configure, self).save()

    def exists(self):
        return self.raw and self.data['passcode_hash']

    def update(self, conf):
        for key in self.data:
            self.data[key] = conf.get(key)


class Theme(FlatFile):

    THEMES_DIR = 'themes'

    STATIC_TYPE = 'page'
    STATIC_TYPE_NAME = 'Pages'

    PRIMARY_MENU = 'primary'
    PRIMARY_MENU_NAME = 'Primary Menu'

    conf_path = 'config.json'

    path = ''
    data = {}

    def __init__(self, theme_name):
        themes_dir = self._abs_path(self.THEMES_DIR)
        self.theme_folder = os.path.join(themes_dir, theme_name)
        self.path = os.path.join(self.theme_folder, self.conf_path)
        super(Theme, self).__init__(self.path)
        self.data = json.loads(self.raw)

    def save(self):
        raise Exception('Save is not allowed.')

    def delete(self):
        raise Exception('Delete is not allowed.')

    @property
    def options(self):
        _options = self.data.get('options') or {}
        return {k: v for k, v in _options.items()}

    @property
    def category(self):
        _category = self.data.get('category') or {}
        if _category:
            category = {
                'name': _category.get('name'),
                'content_type': _category.get('content_type')
            }
        else:
            category = None
        return category

    @property
    def content_types(self):
        _content_types = self.data.get('content_types') or {}
        content_types = {k: {
            'key': k,
            'title': v.get('title') or '',
            'cloaked': bool(v.get('cloaked')),
            'templates': v.get('templates', [k]),
        } for k, v in _content_types.items()}
        if self.STATIC_TYPE not in content_types:
            content_types.update({
                self.STATIC_TYPE: {
                    'key': self.STATIC_TYPE,
                    'title': self.STATIC_TYPE_NAME,
                    'cloaked': False,
                    'templates': [],
                }
            })
        return content_types

    @property
    def templates(self):
        _templates = self.data.get('templates') or []
        return [process_slug(template) for template in _templates]

    @property
    def custom_fields(self):
        _custom_fields = self.data.get('custom_fields') or {}

        def _get_opts(sel_opts):
            selection = []
            for op in sel_opts:
                if isinstance(op, str):
                    value = label = op
                elif isinstance(op, dict):
                    value = op.get('value', '')
                    label = op.get('label', '?')
                else:
                    value = ''
                    label = '?'
                selection.append({'label': label, 'value': value})
            return selection

        def _get_fields(opts):
            fields = {}
            for k, v in opts.items():
                key = process_slug(k).replace('-', '_')
                if k.startswith('!'):
                    continue
                elif isinstance(v, str):
                    fields[key] = {
                        'type': v,
                        'label': k,
                        'props': [],
                        'hidden': [],
                    }
                elif isinstance(v, dict):
                    props = v.get('props', [])[:60]
                    props = [{
                        'key': p['key'],  # sub attr key
                        'label': p.get('label', p['key']),
                        'type': p.get('type', 'text'),  # text/select/switch
                        'value': p.get('value', ''),  # default value
                        'options': _get_opts(p.get('options', []))}  # select
                        for p in props
                        if isinstance(p, dict) and p.get('key')]
                    fields[key] = {
                        'type': v.get('type', ''),
                        'label': v.get('label', k),
                        'props': props,
                        'hidden': v.get('!', [])
                    }
                else:
                    fields[key] = {
                        'type': '',
                        'label': k,
                        'props': [],
                        'hidden': []
                    }
            return fields

        custom_fields = {k: _get_fields(v) for k, v in _custom_fields.items()}
        return custom_fields

    @property
    def hidden_fields(self):
        _custom_fields = self.data.get('custom_fields') or {}

        def _get_hidden_fields(opts):
            return [i for i in opts.get('!', [])]
        hidden_fields = {k: _get_hidden_fields(v)
                         for k, v in _custom_fields.items()}
        return hidden_fields

    @property
    def menus(self):
        _menus = self.data.get('menus') or {}
        menus = {k: {
            'title': v.get('title') or '',
            'level': v.get('level') or 1,
        } for k, v in _menus.items()}
        if self.PRIMARY_MENU not in menus:
            menus.update({
                self.PRIMARY_MENU: {
                    'title': self.PRIMARY_MENU_NAME,
                    'level': 1,
                }
            })
        return menus


class Site(FlatFile):
    CONTENT_DIR = 'content'

    STATIC_TYPE = 'page'
    STATIC_TYPE_NAME = 'Pages'

    PRIMARY_MENU = 'primary'

    DEFUALT_SITE = {
        "app_id": "pyco_app",
        "slug": "pyco",
        "locale": "en_US",
        "content_types": {STATIC_TYPE: STATIC_TYPE_NAME},
        "menus": {PRIMARY_MENU: []},
        "meta": {"title": "Pyco"}
    }

    conf_path = 'site.json'
    data = {}

    def __init__(self):
        self.content_folder = self._abs_path(self.CONTENT_DIR)
        self.path = os.path.join(self.content_folder, self.conf_path)
        super(Site, self).__init__(self.path)
        self._ensure()

    def _ensure(self):
        if self.raw is None:
            self.data = self.DEFUALT_SITE
            self.save()
        self.parse()

    def save(self):
        self.raw = json.dumps(self.data, indent=2, ensure_ascii=False)
        return super(Site, self).save()

    def parse(self):
        site = json.loads(self.raw)
        c_types = site.get('content_types', {})
        if self.STATIC_TYPE not in c_types:
            c_types.update({self.STATIC_TYPE: self.STATIC_TYPE_NAME})
        slots = {k: {
            'name': get_from_dict(v, 'name', str),
            'src': get_from_dict(v, 'src', str),
            'route': get_from_dict(v, 'route', str),
            'scripts': get_from_dict(v, 'scripts', str),
            'data': get_from_dict(v, 'data', dict, default={}),
            'status': bool(v.get('status', True)),
        } for k, v in site.get('slots', {}).items()}

        self._id = site.get('app_id', self._id)
        self.data = {
            '_id': self._id,
            'slug': site.get('slug'),
            'locale': site.get('locale') or 'en_US',
            'content_types': c_types,
            'categories': site.get('categories') or {},
            'menus': site.get('menus') or {self.PRIMARY_MENU: []},
            'slots': slots,
            'meta': site.get('meta') or {},
        }

    @property
    def meta(self):
        _meta = self.data.get('meta') or {}
        return {k: v for k, v in _meta.items()}

    @property
    def content_types(self):
        _content_types = self.data.get('content_types') or {}
        page_type = None
        site_content_types = []
        for k, v in _content_types.items():
            if k == self.STATIC_TYPE:
                page_type = {'key': k, 'title': v}
            else:
                site_content_types.append({'key': k, 'title': v})
        if page_type:
            site_content_types.insert(0, page_type)
        return site_content_types

    @property
    def languages(self):
        lang_list = self.data.get('meta', {}).get('languages') or []
        return [lang for lang in lang_list]

    @property
    def categories(self):
        _categories = self.data.get('categories') or {}
        _terms = _categories.get('terms') or []
        categories = {
            'name': _categories.get('name') or '',
            'content_types': _categories.get('content_types') or [],
            'status': _categories.get('status', 0),
            'terms': [{'key': t.get('key'),
                       'meta': t.get('meta'),
                       'parent': t.get('parent'),
                       'priority': t.get('priority', 1),
                       'status': t.get('status')} for t in _terms]}
        return categories

    @property
    def menus(self):
        _menus = self.data.get('menus') or {}
        menus = [{'key': k, 'nodes': v} for k, v in _menus.items()]

        def _get_index():
            for idx, m in enumerate(menus):
                if m['key'] == self.PRIMARY_MENU:
                    return idx
            return 0
        menus.insert(0, menus.pop(_get_index()))
        return menus

    # methods
    def _uniquify_term_key(self, term_key, term=None):
        term_key = process_slug(term_key)
        if term and term['key'] == term_key:
            return term_key
        all_term_keys = [term['key'] for term in self.categories['terms']]
        if term_key in all_term_keys:
            term_key = self._uniquify_term_key(slug_uuid_suffix(term_key),
                                               term)
        return term_key

    def _find_term(self, term_key):
        for term in self.data['categories'].get('terms', []):
            if term['key'] == term_key:
                return term
        return None

    def _get_term_index(self, terms, term_key):
        if not terms:
            return None
        for idx, m in enumerate(terms):
            if m['key'] == term_key:
                return idx
        return None

    def add_category_term(self, term):
        terms = self.data['categories'].get('terms')
        if not terms:
            self.data['categories']['terms'] = []
        term_meta = term.get('meta') or {}
        term_key = self._uniquify_term_key(term['key'])
        term = {
            'key': term_key,
            'meta': {
                'name': term_meta.get('name', term_key),
                'caption': term_meta.get('caption', ''),
                'figure': term_meta.get('figure', ''),
            },
            'parent': term.get('parent', ''),
            'priority': term.get('priority', 1),
            'status': parse_int(term.get('status')),
        }
        self.data['categories']['terms'].insert(0, term)
        return term

    def get_category_term(self, term_key):
        return self._find_term(term_key)

    def update_category_term(self, term_key, new_term):
        term = self._find_term(term_key)
        if not term:
            raise Exception('Term not found.')
        new_term['key'] = term_key
        term.update(new_term)
        return term

    def remove_category_term(self, term_key):
        terms = self.data['categories'].get('terms') or []
        index = self._get_term_index(terms, term_key)
        if index is None:
            return None
        else:
            terms.pop(index)
        return term_key


class Document(FlatFile):

    CONTENT_DIR = 'content'
    CONTENT_FILE_EXT = '.md'

    MAXIMUM_QUERY = 60
    MAXIMUM_STORAGE = 360

    EXCERPT_LENGTH = 600

    STATIC_TYPE = 'page'

    INDEX_SLUG = 'index'
    SEARCH_SLUG = 'search'
    CATEGORY_SLUG = 'category'
    TAG_SLUG = 'tag'
    ERROR404_SLUG = 'error-404'

    RESERVED_SLUGS = [
        INDEX_SLUG,
        TAG_SLUG,
        CATEGORY_SLUG,
        SEARCH_SLUG,
    ]

    SORTABLE_FIELD_KEYS = ('date', 'updated')
    QUERYABLE_FIELD_KEYS = ('slug', 'parent', 'priority', 'template',
                            'date', 'updated', 'creation')

    STATUS = (STATUS_DRAFT, STATUS_PUBLISHED) = (0, 1)

    path = ''
    data = {}
    _updated = None
    _creation = None

    def __init__(self, path=None):
        if path:
            super(Document, self).__init__(path)
            self.parse()

    def hardcore(self, raw):
        self.raw = raw
        self.parse()

    def add(self, content):
        content_dir = self.get_dir()
        slug = self._uniquify_slug(content['slug'], content['content_type'])
        if content['content_type'] in [None, self.STATIC_TYPE]:
            rel_path = os.path.join(content_dir, slug)
        else:
            rel_path = os.path.join(content_dir,
                                    content['content_type'],
                                    slug)
        self._id = self.path = '{}{}'.format(rel_path, self.CONTENT_FILE_EXT)
        self.data = {
            'slug': slug,
            'meta': content.get('meta', {}),
            'template': content.get('template', ''),
            'parent': content.get('parent', ''),
            'priority': content.get('priority', 1),
            'date': content.get('date', ''),
            'tags': content.get('tags', []),
            'terms': content.get('terms', []),
            'redirect': content.get('redirect', ''),
            'status': parse_int(content.get('status')),
            'content': content.get('content', '')
        }

    def _uniquify_slug(self, slug, content_type, document=None):
        slug = process_slug(slug)
        if document and document.slug == slug:
            return slug
        doc = self.find_one(slug, content_type)
        if doc:
            slug = self._uniquify_slug(slug_uuid_suffix(slug),
                                       content_type,
                                       document)
        return slug

    def save(self):
        _fields = self.data.get('meta') or {}
        _fields.update({
            'template': self.data.get('template', ''),
            'priority': self.data.get('priority', 1),
            'parent': self.data.get('parent', ''),
            'date': self.data.get('date', ''),
            'tags': self.data.get('tags', []),
            'terms': self.data.get('terms', []),
            'redirect': self.data.get('redirect', ''),
            'status': self.data.get('status', self.STATUS_PUBLISHED),
        })

        fields = yaml.safe_dump(self._prepare_field(_fields),
                                stream=None,
                                default_flow_style=False,
                                indent=2,
                                encoding=None,
                                allow_unicode=True)
        content = self.data.get('content') or ''
        self.raw = '/*\n{}\n*/\n{}'.format(fields, content)
        return super(Document, self).save()

    def parse(self):
        self._refresh_time()
        # raw string
        p = r'(\n)*/\*(\n)*(?P<fields>(.*\n)*)\*/(?P<content>(.*(\n)?)*)'
        re_pattern = re.compile(p)
        m = re_pattern.match(self.raw)
        if m is None:
            fields = {}
            content = ''
        else:
            fields = yaml.safe_load(m.group('fields'))
            content = m.group('content').strip('\n\b\r')
            # `.strip('\n\b\r')` use to prevent unexcept empty line.

        self._parse_structure(self._parse_field(fields), content)

    def _parse_structure(self, fields, content):
        tags = [tag.strip().lower() for tag in fields.pop('tags', [])
                if isinstance(tag, str)]
        template = fields.pop('template', self.content_type)
        priority = fields.pop('priority', 1)
        parent = fields.pop('parent', '')
        date = fields.pop('date', '')
        terms = fields.pop('terms', [])
        redirect = fields.pop('redirect', '')
        status = fields.pop('status', self.STATUS_PUBLISHED)

        self.data = {
            '_id': self._id,
            '_keywords': [self.slug] + tags,
            'slug': self.slug,
            'content_type': self.content_type,
            'priority': priority,
            'parent': parent,
            'date': date,
            'tags': tags,
            'terms': terms,
            'redirect': redirect,
            'template': template,
            'status': status,
            'meta': fields,
            'content': content,
            'excerpt': gen_excerpt(content, self.EXCERPT_LENGTH),
            'updated': self._updated,
            'creation': self._creation,
        }

    def _refresh_time(self):
        try:
            self._updated = int(os.path.getmtime(self.path))
            self._creation = int(os.path.getctime(self.path))
        except Exception:
            self._updated = 0
            self._creation = 0

    @property
    def slug(self):
        _path = os.path.splitext(self.path)[0]
        return process_slug(_path.split('/')[-1])

    @property
    def content_type(self):
        path_parts = self.path.split(self.get_dir())[-1].split('/')
        if len(path_parts) > 2:
            content_type = path_parts[1].lower()
        else:
            content_type = self.STATIC_TYPE
        return content_type

    # methods
    @classmethod
    def get_dir(cls):
        if cls.__data_dir__:
            return os.path.join(cls.__data_dir__, cls.CONTENT_DIR)
        return cls.CONTENT_DIR

    @classmethod
    def count(cls):
        file_paths = []
        for path, dirs, files in os.walk(cls.get_dir()):
            for f in files:
                if not f.endswith(cls.CONTENT_FILE_EXT) or f.startswith('_'):
                    continue
                file_paths.append(os.path.join(path, f))
        return len(file_paths[:cls.MAXIMUM_STORAGE])

    @classmethod
    def find_one(cls, slug, content_type=None):
        if content_type in [None, cls.STATIC_TYPE]:
            rel_path = os.path.join(cls.get_dir(), slug)
        else:
            rel_path = os.path.join(cls.get_dir(), content_type, slug)
        path = '{}{}'.format(rel_path, cls.CONTENT_FILE_EXT)
        if os.path.isfile(path):
            return cls(path)
        else:
            return None

    @classmethod
    def find(cls, content_type=None):
        if content_type == cls.STATIC_TYPE:
            f_dir = cls.get_dir()
        else:
            f_dir = os.path.join(cls.get_dir(), content_type)
        file_paths = [os.path.join(f_dir, f) for f in os.listdir(f_dir)
                      if f.endswith(cls.CONTENT_FILE_EXT) and
                      not f.startswith('_')]
        return [cls(f) for f in file_paths[:cls.MAXIMUM_STORAGE]]

    @classmethod
    def find_recent(cls):
        file_paths = []
        for path, dirs, files in os.walk(cls.get_dir()):
            for f in files:
                if not f.endswith(cls.CONTENT_FILE_EXT) or f.startswith('_'):
                    continue
                file_paths.append(os.path.join(path, f))
        files = [cls(f) for f in file_paths[:cls.MAXIMUM_STORAGE]]
        files.sort(key=lambda x: x._updated, reverse=True)
        return files[:6]


class Media():

    UPLOADS_DIR = 'uploads'
    IMAGE_EXTS = ('jpg', 'jpe', 'jpeg', 'png', 'gif', 'svg')

    MAXIMUM_QUERY = 60
    MAXIMUM_STORAGE = 6000

    filename = ''
    path = ''

    _id = None
    _updated = None
    _creation = None

    def __init__(self, path):
        self._id = self.path = path
        self.filename = os.path.basename(path)
        self._refresh_time()

    def _refresh_time(self):
        try:
            self._updated = int(os.path.getmtime(self.path))
            self._creation = int(os.path.getctime(self.path))
        except Exception:
            self._updated = 0
            self._creation = 0

    def delete(self):
        if os.path.isfile(self.path):
            os.remove(self.path)
        return self._id

    # methods
    @classmethod
    def get_dir(cls):
        if cls.__data_dir__:
            return os.path.join(cls.__data_dir__, cls.UPLOADS_DIR)
        return cls.UPLOADS_DIR

    @classmethod
    def count(cls):
        files = [f for f in os.listdir(cls.get_dir())
                 if os.path.isfile(os.path.join(cls.get_dir(), f))]
        return len(files[:cls.MAXIMUM_STORAGE])

    @classmethod
    def find_one(cls, filename):
        file_path = os.path.join(cls.get_dir(), filename)
        if os.path.isfile(file_path):
            return cls(file_path)
        else:
            return None

    @classmethod
    def find(cls):
        uploads_dir = cls.get_dir()
        file_paths = [f for f in os.listdir(uploads_dir)
                      if os.path.isfile(os.path.join(uploads_dir, f)) and
                      not f.startswith('.')]
        files = [cls(f) for f in file_paths[:cls.MAXIMUM_STORAGE]]
        files.sort(key=lambda x: x._updated, reverse=True)
        return files

    @classmethod
    def find_images(cls):
        files = cls.find()
        return [img for img in files if img.info['ext'] in cls.IMAGE_EXTS]

    @property
    def info(self):
        return {
            '_id': self._id,
            'filename': self.filename,
            'ext': split_file_ext(self.filename),
            'type': split_file_type(self.filename),
            'mimetype': guess_mimetype(self.filename),
            'updated': self._updated,
            'creation': self._creation,
            'is_file': os.path.isfile(self.path),
        }
