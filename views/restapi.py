#coding=utf-8
from __future__ import absolute_import

from flask import current_app, request, abort, render_template, redirect
import os

from helpers import (get_param,
                     make_json_response,
                     make_content_response,
                     sortedby)

from .base import BaseView

      

class RestMetaView(BaseView):
    def get(self):
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
        self.init_context(False)

        output = self.view_ctx

        return make_json_response(output, status_code)


class RestContentView(BaseView):
    def _match_cond(self, cond_value, cond_key, target, 
                                opposite = False, force = False):
        if cond_value == '' and not force:
            return cond_key in target != opposite
        elif cond_value is None and not force:
            # if cond_value is None will reverse the opposite,
            # then for the macthed opposite must reverse again. so...
            # alaso supported if the target value really is None.
            return cond_key in target == opposite
        elif cond_key not in target:
            return False

        matched = False
        target_value = target.get(cond_key)
        if isinstance(cond_value, list):
            for cv in cond_value:
                matched = _match_cond(cv, target_value, force = True)
                if matched:
                    break
        elif isinstance(cond_value, bool):
            matched = cond_value == bool(target_value)
        else:
            if isinstance(target_value, list):
                matched = cond_value in target_value
            else:
                matched = cond_value == target_value

        return matched != opposite

    def _query(self, results, conditions):
        SHORT_ATTR_KEY = self.config.get('SHORT_ATTR_KEY')

        for cond in conditions[:10]: # max fields key is 10
            opposite = False
            force = False
            cond_key = None
            cond_value = ''

            if isinstance(cond, basestring):
                cond_key = cond.lower()
            elif isinstance(cond, dict):
                opposite = bool(cond.pop('not', False))
                force = bool(cond.pop('force', False))
                if cond:
                    cond_key = cond.keys()[0]
                    cond_value = cond[cond_key]
                else:
                    continue
            
            if cond_key is None:
                continue

            cond_key = SHORT_ATTR_KEY.get(cond_key, cond_key)
            
            results = [i for i in results if self._match_cond(cond_value,
                                                              cond_key,
                                                              i,
                                                              opposite,
                                                              force)]
        return results
            
    
    def post(self):
        param_fields = get_param('fields', False, [])
        param_attrs = get_param('metas', False, [])
        param_length = get_param('length', False)
        param_sortby = get_param('sortby', False)
        param_desc = get_param('desc', False, True)
        param_priority = get_param('priority', False, True)
        
        conditions = param_fields + param_attrs
        
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
        
        SHORT_ATTR_KEY = config.get('SHORT_ATTR_KEY')

        theme_meta_options = self.view_ctx["theme_meta"].get('options', {})

        # set default params
        if not param_sortby:
            param_sortby = theme_meta_options.get('sortby', 'updated')
            if isinstance(param_sortby, basestring):
                param_sortby = [param_sortby]
            elif not isinstance(param_sortby, list):
                param_sortby = None
        if not param_length:
            param_length = theme_meta_options.get('perpage', 12)
        
        
        # contents
        self.view_ctx["pages"] = self.get_pages()

        run_hook("get_pages",
                 pages=self.view_ctx["pages"],
                 current_page={})

        results = self._query(self.view_ctx["pages"], conditions)
        
        # sortedby
        sort_keys = []
        if param_priority:
            sort_keys = ['-priority'] if param_desc else ['priority']
        
        if isinstance(param_sortby, basestring):
            sort_keys.append(param_sortby)
        elif isinstance(param_sortby, list):
            sort_keys = sort_keys + [SHORT_ATTR_KEY.get(key, key)
                                     for key in param_sortby
                                     if isinstance(key, basestring)]
    
        results = sortedby(results, sort_keys, param_desc)
        
        
        # length
        if param_length > 0:
            results = results[0:param_length]
        
        output = results

        return make_json_response(output, status_code)