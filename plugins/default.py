# coding=utf-8

import re

loaded_config = None


def config_loaded(config):
    loaded_config = config
    return loaded_config


def request_url(request):
    pass


def get_page_content(content):
    content['content'] = shortcode(loaded_config, content['text'])


def get_page_meta(page_meta, redirect):
    shortcode(page_meta)


def get_pages(pages, current_page_id):
    shortcode(pages)


def before_render(context, template):
    pass


def after_render(rendered):
    pass


# shortcode
re_uploads_dir = re.compile(r'\[\%uploads\%\]', re.IGNORECASE)
re_theme_dir = re.compile(r'\[\%theme\%\]', re.IGNORECASE)


def _process_shortcode(config, text):
    text = re.sub(re_uploads_dir, str(config['UPLOADS_URL']), text)
    text = re.sub(re_theme_dir, str(config['THEME_URL']), text)


def shortcode(config, data):
    if isinstance(data, str):
        _process_shortcode(data)
    elif isinstance(data, list):
        for item in data:
            _process_shortcode(item)
    elif isinstance(data, dict):
        for k, v in data:
            _process_shortcode(v)
