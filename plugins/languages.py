# coding=utf-8
from __future__ import absolute_import

import os
from flask import current_app, g

from plugins.i18n import Translator


_TRANSLATE_REDIRECT = False
_TRANSLATES = {}
_LANGUAGES_FOLDER = 'languages'
_TRANS_FILE = 'translate'


def config_loaded(config):
    global _TRANSLATES
    site_meta = config.get("SITE", {}).get("meta", {})
    _TRANSLATES = site_meta.pop("translates", None)
    return


def before_render(var, template):
    """ translates json sample
    {
       "zh_CN":{"name":"汉语","url":"http://....."},
       "en_US":{"name":"English","url":"http://....."}
    }
    """
    trans_list = []
    locale = g.curr_app["locale"]
    lang = locale.split('_')[0]
    translates = _TRANSLATES

    if translates:
        if isinstance(translates, list):
            # directly append if is list
            trans_list = [trans for trans in translates if trans.get('key')]

        elif isinstance(translates, dict):
            # change to list if is dict
            def _make_key(k, v):
                v.update({"key": k})
                return v
            trans_list = [_make_key(k, v) for k, v in translates.iteritems()]

    for trans in trans_list:
        trans_key = trans['key'].lower()
        if trans_key == locale.lower() or trans_key == lang.lower():
            trans["active"] = True

    var["translates"] = trans_list
    var["locale"] = locale
    var["lang"] = lang

    # set current translates
    lang_path = os.path.join(current_app.template_folder, _LANGUAGES_FOLDER)

    translator = Translator(locale, lang_path)
    var['_'] = translator.gettext
    var['_t'] = translator.t_gettext

    return
