#coding=utf-8
from __future__ import absolute_import
import gettext
import os
from flask import current_app

_DEFAULT_LOCALE = 'en'
_TRANSLATE_REDIRECT = False
_LOCALE = None
_TRANSLATES = {}
_LANGUAGES_FOLDER = 'languages'
_TRANS_FILE = 'translate'


def config_loaded(config):
    global _LOCALE, _TRANSLATES
    site_meta = config.get("SITE", {}).get("meta", {})
    _LOCALE = site_meta.get("locale", _DEFAULT_LOCALE)
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
    locale = _LOCALE
    lang = locale.split('_')[0]
    translates = _TRANSLATES
    
    if translates:
        # directly append if is list
        if isinstance(translates, list):
            for trans in translates:
                if trans.get('key'):
                    trans_list.append(trans)

        # change to list if is dict
        if isinstance(translates, dict):
            for trans in translates:
                tmp_trans = translates[trans]
                tmp_trans.update({"key": trans})
                trans_list.append(tmp_trans)
    

    for trans in trans_list:
        trans_key = trans['key'].lower()
        if trans_key == locale.lower() or trans_key == lang.lower():
            trans["active"] = True
    
    set_current_translation(_LOCALE)
    
    var["translates"] = trans_list
    var["locale"] = locale
    var["lang"] = lang
    return


# custome functions
def set_current_translation(locale):
    if locale and isinstance(locale,(str,unicode)):
        lang_path = os.path.join(current_app.template_folder,
                                 _LANGUAGES_FOLDER)

        tr = gettext.translation(_TRANS_FILE, lang_path, 
                                 languages=[locale], fallback=True)
        
        current_app.jinja_env.install_gettext_translations(tr, newstyle=True)