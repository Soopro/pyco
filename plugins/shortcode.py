#coding=utf-8
from __future__ import absolute_import
import re

_CONFIG = {}
_DEFAULT_SHORTCODES  = [
    {"pattern":"base_url","replacement":""},
    {"pattern":"uploads","replacement":"/uploads"}
]
_SHORTCODES = None

def config_loaded(config):
    global _CONFIG,_SHORTCODES

    _CONFIG = config
    shortcodes = _CONFIG.get("SHORTCODES",_DEFAULT_SHORTCODES)
    if shortcodes:
        _SHORTCODES = [code for code in shortcodes if code.get("pattern")]
    return


def after_read_page_meta(headers):
    filter_meta_shortcode(headers)
    return

def before_parse_content(content):
    filter_content_shortcode(content)
    return   

#custom functions
def filter_meta_shortcode(meta):
    for k in meta:
        for code in _SHORTCODES:
            pattern = make_pattern(code["pattern"])
            meta[k] = re.sub(pattern, code["replacement"], meta[k])


def filter_content_shortcode(content):
    for code in _SHORTCODES:
        pattern = make_pattern(code["pattern"])
        content["content"] = re.sub(pattern, code.get("replacement"), content["content"])


def make_pattern(pattern):
    return re.compile(r"%\s*{}\s*%".format(pattern), re.IGNORECASE)