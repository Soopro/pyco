#coding=utf-8
from __future__ import absolute_import

from flask import current_app, request, abort, render_template, redirect, g
import os

from helpers import (get_param,
                     make_json_response,
                     helper_make_dotted_dict,
                     helper_process_url)

from .base import BaseView


class RestMetaView(BaseView):
    def get(self):
        # init
        config = self.config
        status_code = 200
        is_not_found = False
        run_hook = self.run_hook
        
        #for pass intor hook
        file = {"path": None}
        file_content = {"content": None}
        
        # load
        self.load_metas()
        self.load_plugins(config.get("PLUGINS"))
        run_hook("plugins_loaded")

        current_app.debug = config.get("DEBUG")
        self.init_context()

        output = self.view_ctx

        return make_json_response(output, status_code)


class RestContentView(BaseView):
    def post(self):
        param_fields = get_param('fields', False, [])
        param_attrs = get_param('metas', False, [])
        param_length = get_param('length' False, 0)
        param_sortby = get_param('sortby', False)
        param_desc = get_param('desc', False, True)
        param_priority = get_param('priority', False, True)
        
        # init
        config = self.config
        status_code = 200
        is_not_found = False
        run_hook = self.run_hook
        
        # load
        self.load_metas()
        self.load_plugins(config.get("PLUGINS"))
        run_hook("plugins_loaded")
        
        current_app.debug = config.get("DEBUG") 
        self.init_context()

        run_hook("config_loaded", config=self.config)
        
        base_url = config.get("BASE_URL")
        charset = config.get('CHARSET')
        
        # content
        pages = self.get_pages()
        self.view_ctx["pages"] = pages

        run_hook("get_pages",
                 pages=self.view_ctx["pages"],
                 current_page={})
        
        results = self.view_ctx["pages"]
        
        # sortedby
        sort_keys = []

        if param_priority:
            sort_keys = ['-priority'] if desc else ['priority']
        
        if isinstance(sort_by, basestring):
            sort_keys.append(sort_by)
        elif isinstance(sort_by, list):
            sort_keys = sort_keys + [key for key in sort_by 
                                     if isinstance(key, basestring)]
    
        return sortedby(results, sort_keys, param_desc)
        
        
        # length
        if param_legnth > 0:
            results = results[0:param_legnth]
        
        output = pages
        
        return make_json_response(output, status_code)