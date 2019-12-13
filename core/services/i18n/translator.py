# coding=utf-8

# ---------------------
# Simplify i18n Translator
#
# Author : Redy Ru
# Email : redy.ru@gmail.com
# License : MIT
#
# Methods & Parameters:
# - Translate: init with current locale language,
#   `locale` -> the local language code .
#   `source` -> where is dictionary, could be the dir of translate files
#               or dict and list.
#   `case_sensitive` -> to ignore cases.
# - load: load translate dictionary as new.
#   `source` -> dictionary source again.
# - append: add new dictionary in the the old one.old
#   `source` -> dictionary source again.
# - empty: clean up the translate dictionary already loaded.
# - gettext: translate a word, expose it to template context.
#   `<word>` -> the word you need translate.word
#   `<*replacement>` -> replace those text into '%s' in the translate word.
# - t_gettext: translate dict of word which is define by it self.
#   `<dict>` -> a dict with word or language definition. {'en': 'Word'}
# ---------------------

import os
import json


class Translator(object):

    locale = 'en'
    lang = 'en'
    dictionary = dict()
    case_sensitive = False

    def __init__(self, locale, source=None, case_sensitive=False):
        if isinstance(locale, str):
            self.locale = locale
            self.lang = locale.split('_')[0]
        self.case_sensitive = bool(case_sensitive)
        if source:
            self.load(source)

    def _trans_key(self, text):
        return text if self.case_sensitive else text.lower()

    def _parse_path(self, lang_dir):
        path = os.path.join(lang_dir, '{}.lang'.format(self.locale))
        if not os.path.isfile(path):
            path = os.path.join(lang_dir, '{}.lang'.format(self.lang))
        if not os.path.isfile(path):
            path = None
        return path

    def _load_file(self, lang_dir):
        path = self._parse_path(lang_dir)
        if not path:
            return {}
        try:
            with open(path) as f:
                source = json.load(f)
        except Exception as e:
            raise IOError('i18n: Invalid dictionary file. {}'.format(e))
        return source

    def _load(self, source=None):
        dictionary = {}
        if isinstance(source, str):
            source = self._load_file(source)

        if isinstance(source, list):
            for msg in source:
                msgid = msg.get('msgid')
                msgstr = msg.get('msgstr')
                if msgid:
                    dictionary.update({self._trans_key(msgid): msgstr})
        elif isinstance(source, dict):
            for k, v in source.items():
                msgid = k
                msgstr = v
                if msgid:
                    dictionary.update({self._trans_key(msgid): msgstr})
        else:
            raise TypeError('i18n: Invalid dictionary type.')

        return dictionary

    def load(self, source):
        # load will replace old dictionary
        self.dictionary = self._load(source)

    def append(self, source):
        # load will replace old dictionary
        self.dictionary.update(self._load(source))

    def empty(self):
        # empty dictionary
        self.dictionary = {}

    def gettext(self, text, *args):
        if not isinstance(text, str):
            return text

        trans = self.dictionary.get(self._trans_key(text), text)

        for arg in args:
            trans = trans.replace('%s', str(arg), 1)

        return trans

    def t_gettext(self, text_dict):
        if not text_dict or not isinstance(text_dict, dict):
            trans = text_dict
        elif self.locale:
            trans = text_dict.get(self.locale) or text_dict.get(self.lang)
        else:
            trans = next(iter(text_dict.values()))
        return trans
