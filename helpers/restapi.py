# coding=utf8
from flask import current_app, request

from helpers.common import load_metas, load_plugins, run_hook, init_context
from utils.misc import sortedby, make_json_response


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


def get_rest_meta():
    # init
    status_code = 200

    config = current_app.config

    # load
    load_metas()
    plugins = load_plugins(config.get("PLUGINS"))
    run_hook(plugins, "plugins_loaded")

    current_app.debug = config.get("DEBUG")
    view_ctx = init_context(request, config, False)

    run_hook("config_loaded", config=config)
    run_hook("before_render", var=view_ctx, template=None)

    output = view_ctx

    return make_json_response(output, status_code)


def _add_pagination(content_file, index, total_count):
    content_file['pagination'] = {
        'num': index + 1,
        'index': index,
        'total_count': total_count,
        'has_more': total_count - 1 > index,
    }
    return content_file