# coding=utf-8

import re

plugin_data = {}


def config_loaded(config):
    plugin_data['config'] = config


def request_url(request):
    pass


def get_page_content(content):
    content['content'] = shortcode(plugin_data['config'], content['content'])


def get_page_meta(meta, redirect):
    shortcode(plugin_data['config'], meta)


def get_pages(pages, current_page_id):
    shortcode(plugin_data['config'], pages)


def before_render(context, template):
    pass


def after_render(rendered):
    pass


# shortcode
RE_UPLOADS = re.compile(r'\[\%uploads\%\]', re.IGNORECASE)
RE_THEME = re.compile(r'\[\%theme\%\]', re.IGNORECASE)


def _process_shortcode(config, text):
    print(text)
    print('---------------------------')
    text = re.sub(RE_UPLOADS, str(config['UPLOADS_URL']), text)
    text = re.sub(RE_THEME, str(config['THEME_URL']), text)


def shortcode(config, data):
    if isinstance(data, str):
        _process_shortcode(config, data)
    elif isinstance(data, list):
        for item in data:
            shortcode(config, item)
    elif isinstance(data, dict):
        for k, v in data.items():
            shortcode(config, v)
