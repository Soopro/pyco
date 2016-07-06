# coding=utf-8
from __future__ import absolute_import

from flask import current_app

from helpers import (get_param,
                     get_args,
                     make_json_response,
                     sortedby)

from .base import BaseView


class RestMetaView(BaseView):
    def get(self):
        # init
        config = self.config
        status_code = 200
        run_hook = self.run_hook

        # load
        self.load_metas()
        self.load_plugins(config.get("PLUGINS"))
        run_hook("plugins_loaded")

        current_app.debug = config.get("DEBUG")
        self.init_context(False)

        run_hook("config_loaded", config=self.config)
        run_hook("before_render", var=self.view_ctx, template=None)

        output = self.view_ctx

        return make_json_response(output, status_code)


class RestContentView(BaseView):
    MAXIMUM_QUERY = 60

    def _match(self, target, cond_key, cond_value,
               opposite=False, force=False):
        if cond_value == '' and not force:
            return cond_key in target != opposite
        elif cond_value is None and not force:
            # if cond_value is None will reverse the opposite,
            # then for the macthed opposite must reverse again. so...
            # also supported if the target value really is None.
            return cond_key in target == opposite
        elif cond_key not in target:
            return False

        matched = False
        target_value = target.get(cond_key)
        if isinstance(cond_value, list):
            for c_val in cond_value:
                matched = self._match(target, cond_key, c_val, force=True)
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

    def _query(self, results, conditions=[], sortby=None,
               priority=None, desc=None):
        SHORT_ATTR_KEY = self.config.get('SHORT_ATTR_KEY')

        for cond in conditions[:10]:  # max fields key is 10
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
            results = [i for i in results
                       if self._match(i, cond_key, cond_value,
                                      opposite, force)]
        # sortedby
        sort_keys = []
        if priority:
            sort_keys = ['-priority'] if desc else ['priority']
        if isinstance(sortby, basestring):
            sort_keys.append(sortby)
        elif isinstance(sortby, list):
            sort_keys = sort_keys + [SHORT_ATTR_KEY.get(key, key)
                                     for key in sortby
                                     if isinstance(key, basestring)]
        if sort_keys:
            results = sortedby(results, sort_keys, desc)

        return results

    def post(self):
        param_fields = get_param('fields', False, [])
        param_metas = get_param('metas', False, [])
        param_sortby = get_param('sortby', False, [])
        param_limit = get_param('limit', False, 0)
        param_offset = get_param('offset', False, 0)
        param_desc = get_param('desc', False, True)
        param_priority = get_param('priority', False, True)

        # init
        config = self.config
        status_code = 200
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
                param_sortby = []

        if not param_limit:
            param_limit = theme_meta_options.get('perpage', 12)

        # contents
        self.view_ctx["pages"] = self.get_pages()

        run_hook("get_pages",
                 pages=self.view_ctx["pages"],
                 current_page={})

        run_hook("before_render", var=self.view_ctx, template=None)

        # make conditions
        conditions = param_fields + param_metas

        # query from contents
        results = self._query(self.view_ctx["pages"],
                              conditions,
                              param_sortby,
                              param_priority,
                              param_desc)
        # offset
        offset = param_offset if param_offset > 0 else 0
        # length
        length = param_limit if param_limit > 0 else self.MAXIMUM_QUERY
        length = max(length, self.MAXIMUM_QUERY)

        # resutls
        total_count = len(resutls)
        results = results[offset:length]
        output = {
            "results": results,
            "count": len(results),
            "total_count": total_count,
        }
        return make_json_response(output, status_code)

    def _add_pagination(content_file, index, total_count):
        content_file['pagination'] = {
            'num': index + 1,
            'index': index,
            'total_count': total_count,
            'has_more': total_count - 1 > index,
        }
        return content_file

    def get(self, type_slug=None):
        limit = get_args('limit', default=0)
        offset = get_args('offset', default=0)

        # init
        config = self.config
        status_code = 200
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

        # contents
        self.view_ctx["pages"] = self.get_pages()

        run_hook("get_pages",
                 pages=self.view_ctx["pages"],
                 current_page={})

        run_hook("before_render", var=self.view_ctx, template=None)

        # make conditions
        if type_slug:
            conditions = [{"content_type": type_slug}]

        # query from contents
        results = self._query(self.view_ctx["pages"], conditions)

        # offset
        offset = param_offset if param_offset > 0 else 0
        # length
        length = param_limit if param_limit > 0 else self.MAXIMUM_QUERY
        length = max(length, self.MAXIMUM_QUERY)

        # resutls
        total_count = len(resutls)
        curr_index = offset
        output = []
        for f in results[offset:length]:
            output.append(self._add_pagination(f, curr_index, total_count))
            curr_index += 1
        return make_json_response(output, status_code)
