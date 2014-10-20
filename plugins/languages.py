#coding=utf-8
from __future__ import absolute_import

_DEFAULT_LOCALE = 'en'
_TRANSLATE_REDIRECT = False
_LOCALE = None
_TRANSLATES = None
_current_lang = None

def config_loaded(config):
    global _LOCALE, _TRANSLATES, _TRANSLATE_REDIRECT
    _LOCALE = config.get("LOCALE") or _DEFAULT_LOCALE
    _TRANSLATES = config.get("TRANSLATES")
    _TRANSLATE_REDIRECT = config.get("TRANSLATE_REDIRECT")
    return

def request_url(request, redirect_to):
    global _current_lang
    accept_languages = request.accept_languages
    _current_lang = _LOCALE
    for lang in accept_languages:
        for trans in _TRANSLATES:
            if str(lang).find(trans) > 0:
                _current_lang = trans
                break
        break

    if _current_lang != _LOCALE and _TRANSLATE_REDIRECT:
        trans = _TRANSLATES[_current_lang]
        redirect_to["url"]=trans.get("url")
    return

def before_render(var,template):
    current_trans = _TRANSLATES[_current_lang]
    translates = [_TRANSLATES[trans] for trans in _TRANSLATES]
    var["translates"] = translates
    var["language_text"] = current_trans["text"]
    var["locale"] = _LOCALE
    return