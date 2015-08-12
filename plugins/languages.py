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
_TRANS_FILE = 'translate'


def config_loaded(config):
    global _LOCALE, _TRANSLATES
    site_meta = config.get("SITE", {}).get("meta", {})
    _LOCALE = site_meta.get("locale", _DEFAULT_LOCALE)
    _TRANSLATES = site_meta.get("translates")
    return


def request_url(request, redirect_to):
    if _TRANSLATES:
        global _current_lang
        _current_lang = request.accept_languages.best_match(_TRANSLATES.keys())
    return


def before_render(var, template):
    """ translates json sample
    {
       "zh_CN":{"name":"汉语","url":"http://....."},
       "en_US":{"name":"English","url":"http://....."}
    }
    """
    trans_list = []
    
    if _TRANSLATES:
        translates = _TRANSLATES
        
        # directly append if is list
        if isinstance(translates, list):
            for trans in translates:
                if trans.get('code'):
                    trans_list.append(trans)

        # change to list if is dict
        if isinstance(translates, dict) and len(translates) > 1:
            for trans in translates:
                tmp_trans = translates[trans]
                tmp_trans.update({"code": trans})
                trans_list.append(tmp_trans)

    set_current_translation(_LOCALE)
    
    var["translates"] = trans_list
    var["locale"] = _LOCALE
    var["lang"] = _LOCALE.split('_')[0]
    return


# custome functions
def set_current_translation(locale):
    if locale and isinstance(locale,(str,unicode)):
        lang_path = os.path.join(current_app.template_folder,
                                 _LANGUAGES_FOLDER)

        tr = gettext.translation(_TRANS_FILE, lang_path, 
                                 languages=[locale], fallback=False)
        
        current_app.jinja_env.install_gettext_translations(tr, newstyle=True)