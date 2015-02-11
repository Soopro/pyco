#coding=utf-8
from __future__ import absolute_import
import gettext
import os
from flask import current_app

_DEFAULT_LOCALE = 'en'
_TRANSLATE_REDIRECT = False
_LOCALE = None
_TRANSLATES = {}
_current_lang = None
_LANGUAGES_FOLDER = 'languages'
_THEME_NAME = None


def config_loaded(config):
    global _LOCALE, _TRANSLATES, _THEME_NAME
    site_meta = config.get("SITE_META", {})
    _THEME_NAME = config.get("THEME_NAME")
    _LOCALE = site_meta.get("locale", _DEFAULT_LOCALE)
    _TRANSLATES = site_meta.get("translates")
    return


def request_url(request, redirect_to):
    if _TRANSLATES:
        global _current_lang
        _current_lang = request.accept_languages.best_match(_TRANSLATES.keys())
    return


def before_render(var, template):
    if _TRANSLATES:
        set_current_translation(_LOCALE)
        current_trans = _TRANSLATES[_current_lang]
        translates = []
        for trans in _TRANSLATES:
            tmp_trans = _TRANSLATES[trans]
            tmp_trans.update({"code": trans})
            translates.append(tmp_trans)
        
        var["translates"] = translates
        var["language_text"] = current_trans["text"]
    
    var["locale"] = _LOCALE
    var["lang"] = _LOCALE.split('_')[0]
    return


# custome functions
def set_current_translation(lang):
    if _TRANSLATES and _THEME_NAME:
        lang_path = os.path.join(current_app.template_folder,
                                 _LANGUAGES_FOLDER)
        tr = gettext.translation(_THEME_NAME, 
                                 lang_path, languages=[lang], fallback=False)
        
        current_app.jinja_env.install_gettext_translations(tr)