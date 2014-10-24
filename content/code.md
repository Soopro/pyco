/*
Title: Code View
Date: 2014/01/01
Nav: Code Test
Order: 0
Tagline: Code View
Template: post
*/

#### This is looks like Python
***
	:::html
	<test>sdfasdf</test>
***

	:::python
	    #theme
	    @property
	    def theme_name(self):
	        return self.config.get("THEME_NAME")

	    def theme_path_for(self, tmpl_name):
	        return "{}{}".format(tmpl_name, TEMPLATE_FILE_EXT)
	        # return os.path.join(self.theme_name, "{}{}".format(tmpl_name, TEMPLATE_FILE_EXT))

		#coding=utf-8
		from __future__ import absolute_import

		DEBUG = False
		PORT = 5000
		AUTO_INDEX = False

		SITE_TITLE = "TEST"
		BASE_URL = "http://localhost:5000"
		SITE_AUTHOR = "DTynn"
		SITE_DESCRIPTION = "123123"

		LOCALE = "en"

		POST_DATE_FORMAT = "%d, %b %Y"

		POST_ORDER_BY = "date"
		POST_ORDER = "desc"

		IGNORE_FILES = []

		THEME_NAME = "default"
		PLUGINS = ["additional_metas","shortcode","redirect","argments","draft",
		"content_types","sort_by_order","languages"]

		""" For Plugins """
		#languages
		TRANSLATES = {"en":{"name":u"English", "text":u"Language", "url":u"http://smalltalks.cc"},
			"zh":{"name":u"简体中文", "text":u"语 言", "url":u"http://cn.smalltalks.cc"}}
		TRANSLATE_REDIRECT = False
		#shortcodes
		SHORTCODES  = [
		    {"pattern":"base_url","replacement":""},
		    {"pattern":"uploads","replacement":"/uploads"},
		    {"pattern":"image_url","replacement":"/uploads"}
		]

		ADDITIONAL_METAS = ["nav","link","target","parent","thumbnail"]