#coding=utf-8
from __future__ import absolute_import

_CONFIG = {}


def config_loaded(config):
    global _CONFIG
    _CONFIG = config
    return

def before_render(var, template):
    if not var["meta"].get("template"):
        template["file"] = var["meta"].get("type")
    return
