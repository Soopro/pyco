# coding=utf-8
from __future__ import absolute_import

import os
import json


class Translator(object):

    locale = 'en'
    lang = 'en'
    charset = 'utf-8'
    dictionary = dict()
    case_sensitive = False

    def __init__(self, locale, loc_dict=None,
                 case_sensitive=False, charset=None):
        if isinstance(locale, basestring):
            self.locale = locale
            self.lang = locale.split('_')[0]
        if charset:
            self.charset = charset
        if loc_dict:
            self.load(loc_dict, case_sensitive)

    def _unicode(self, text):
        if isinstance(text, str):
            text = text.decode(self.charset)
        else:
            try:
                # int, float, long, complex, etc.
                text = unicode(text)
            except Exception:
                text = u''
        return text

    def _trans_key(self, text):
        return text if self.case_sensitive else text.lower()

    def _parse_path(self, lang_folder):
        path = os.path.join(lang_folder, self.locale)
        if not os.path.isfile(path):
            path = os.path.join(lang_folder, '{}.lang'.format(self.lang))
        if not os.path.isfile(path):
            path = None
        return path

    def _load_file(self, path):
        path = self._parse_path(path)
        try:
            with open(path) as f:
                dictionary = json.load(f)
            assert isinstance(dictionary, list)
        except Exception as e:
            raise IOError(u'i18n: Invalid dictionary file. {}'.format(e))
        return dictionary

    def load(self, dictionary=None, case_sensitive=False):
        self.dictionary = {}  # reset dictionary

        if isinstance(dictionary, basestring):
            dictionary = self._load_file(dictionary)

        self.case_sensitive = bool(case_sensitive)

        if isinstance(dictionary, list):
            for msg in dictionary:
                msgid = self._unicode(msg.get('msgid'))
                msgstr = self._unicode(msg.get('msgstr'))
                if msgid:
                    self.dictionary.update({self._trans_key(msgid): msgstr})

        elif isinstance(dictionary, dict):
            for k, v in dictionary.iteritems():
                msgid = self._unicode(k)
                msgstr = self._unicode(v)
                if msgid:
                    self.dictionary.update({self._trans_key(msgid): msgstr})

        else:
            raise TypeError('i18n: Invalid dictionary type.')

    def gettext(self, text, *args):
        if not isinstance(text, basestring):
            return text

        text = self._unicode(text)
        trans = self.dictionary.get(self._trans_key(text), text)

        for arg in args:
            arg = self._unicode(arg)
            trans = trans.replace('%s', arg, 1)

        return trans

    def t_gettext(self, text_dict):
        if not text_dict or not isinstance(text_dict, dict):
            trans = text_dict
        elif self.locale:
            trans = text_dict.get(self.locale) or text_dict.get(self.lang)
        else:
            trans = text_dict.itervalues().next()
        return self._unicode(trans)
