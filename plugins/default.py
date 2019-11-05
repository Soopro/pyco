# coding=utf-8

import re

CONTEXT = {}


def config_loaded(config):
    CONTEXT['config'] = config


def request_url(request):
    pass


def get_page_content(pack):
    pack.update({
        'content': shortcode(CONTEXT['config'], pack['content'])
    })


def get_page_meta(meta, redirect):
    meta.update(shortcode(CONTEXT['config'], meta))


def get_pages(pages, current_page_id):
    for p in pages:
        p.update(shortcode(CONTEXT['config'], p))


def before_render(context, template):
    pass


def after_render(rendered):
    pass


# shortcode
RE_UPLOADS = re.compile(r'\[\%uploads\%\]', re.IGNORECASE)
RE_THEME = re.compile(r'\[\%theme\%\]', re.IGNORECASE)


def _process_shortcode(config, text):
    text = re.sub(RE_UPLOADS, str(config['UPLOADS_URL']), text)
    text = re.sub(RE_THEME, str(config['THEME_URL']), text)
    return text


def shortcode(config, data):
    if isinstance(data, str):
        return _process_shortcode(config, data)
    elif isinstance(data, list):
        return [shortcode(config, item) for item in data]
    elif isinstance(data, dict):
        return {k: shortcode(config, v) for k, v in data.items()}
    else:
        return data
