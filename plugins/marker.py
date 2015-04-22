#coding=utf-8
from __future__ import absolute_import
import os, re, time

uploads_pattern = r"\/\$uploads\/"
_CONFIG = {}

def config_loaded(config):
    global _CONFIG
    _CONFIG = config
    # for key in config:
    #     config[key] = parser_config(config[key])
    # _CONFIG = config

    return

def after_render(output):
    output["content"] = replace(output["content"])
    return

# custom functions
def replace(content):
    uploads_dir = os.path.join(_CONFIG["BASE_URL"], _CONFIG["UPLOADS_DIR"], "")
    re_uploads_dir = re.compile(uploads_pattern, re.IGNORECASE)
    return re.sub(re_uploads_dir, uploads_dir, content)
    
# def parser_config(config):
#     if isinstance(config, (dict, list)):
#         obj = config if isinstance(config, dict) else xrange(len(config))
#         for i in obj:
#             config[i] = parser_config(config[i])
#     elif isinstance(config, (str, unicode)):
#         config = replace(config)
#     return config