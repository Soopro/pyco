# coding=utf-8
from __future__ import absolute_import

import os
import json


class Translator(object):

    locale = 'en'
    lang = 'en'
    charset_utf8 = 'utf-8'
    use_unicode = True
    dictionary = dict()
    case_sensitive = False

    def __init__(self, locale, loc_dict=None,
                 case=False, force=False, use_unicode=True):
        if isinstance(locale, basestring):
            self.locale = locale
            self.lang = locale.split('_')[0]
        if loc_dict:
            self.load(loc_dict, case, force)

    def _encode(self, text):
        if not isinstance(text, basestring):
            text = ''
        elif isinstance(text, (int, float, long, complex)):
            text = unicode(text)

        if not isinstance(text, unicode) and self.use_unicode:
            text = text.decode(self.charset_utf8)
        elif isinstance(text, unicode) and not self.use_unicode:
            text = text.encode(self.charset_utf8)

        return text

    def _trans_key(self, text):
        return text if self.case_sensitive else text.lower()

    def _all_basestring(self, *args):
        for arg in args:
            if not isinstance(arg, basestring):
                return False
        return True

    def _parse_path(self, lang_folder):
        path = os.path.join(lang_folder, self.locale)
        if not os.path.isfile(path):
            path = os.path.join(lang_folder, '{}.lang'.format(self.lang))
        if not os.path.isfile(path):
            path = None
        return path

    def _load_file(self, path, force=False):
        path = self._parse_path(path)
        if not path and not force:
            return {}  # set emtpy dict for translator
        try:
            with open(path) as f:
                dictionary = json.load(f)
            assert isinstance(dictionary, list)
        except Exception as e:
            raise IOError('i18n: Invalid dictionary file.')
        return dictionary

    def load(self, dictionary=None, case_sensitive=False, force=False):
        self.dictionary = {}  # reset dictionary

        if isinstance(dictionary, basestring):
            dictionary = self._load_file(dictionary, force)

        self.case_sensitive = bool(case_sensitive)

        if isinstance(dictionary, list):
            for msg in dictionary:
                msgid = msg.get('msgid')
                msgstr = msg.get('msgstr')

                if not self._all_basestring(msgid, msgstr) or not msgid:
                    continue
                msgid = self._encode(msgid)
                msgstr = self._encode(msgstr)

                if msgid and isinstance(msgid, basestring) \
                        and isinstance(msgstr, basestring):
                    self.dictionary.update({self._trans_key(msgid): msgstr})

        elif isinstance(dictionary, dict):
            for k, v in dictionary.iteritems():
                if not self._all_basestring(k, v) or not k:
                    continue
                msgid = self._encode(k)
                msgstr = self._encode(v)
                self.dictionary.update({self._trans_key(msgid): msgstr})

        else:
            raise TypeError('i18n: Invalid dictionary type.')

    def gettext(self, text, *args):
        if not isinstance(text, basestring):
            return text

        text = self._encode(text)

        trans = self.dictionary.get(self._trans_key(text), text)
        trans = self._encode(trans)

        for arg in args:
            if not isinstance(arg, basestring):
                continue
            arg = self._encode(arg)
            trans = trans.replace('%s', arg, 1)

        return trans

    def t_gettext(self, text_dict):
        if not text_dict or not isinstance(text_dict, dict):
            trans = text_dict
        elif self.locale:
            trans = text_dict.get(self.locale) or text_dict.get(self.lang)
        else:
            trans = text_dict.itervalues().next()
        return self._encode(trans)
