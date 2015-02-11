#coding=utf-8
from __future__ import absolute_import
HOST = '0.0.0.0'
DEBUG = True
PORT = 5500

THEME_NAME = 'default'

BASE_URL = "http://127.0.0.1:5500/"

SITE_META = {
    "title": "DevinPan",
    "author": "pan",
    "description": "A invincible super high-end photographer devin pan's website",
    "copyright": "&copy; devinPan.com",
    "license": "#license",
    "locale": "zh_CN"
}

THEME_META = {
	"alias":"tinforce",
	"title":"Tinforce Theme",
	"thumbnail":"tinforce.png",
	"previews":[],
	"description":"It's for Tinforce digital design studio. A simple profolio website, host most of our works.",
	
    "templates":{
    "index":"Homepage",
    "page":"Page",
    "works":"Works",
    "error_404":"404"
    },
  
    "options":{
    	"sortby":"date",
    	"excerpt_length":162,
    	"excerpt_ellipsis":"&hellip;",
    	"date_format": "%B %d, %Y",
    	"perpage":12,
    "markdown": False
    }
}

PAGE_DATE_FORMAT = "%d, %b %Y"

PAGE_ORDER_BY = "date"
PAGE_ORDER = "desc"

IGNORE_FILES = []

PLUGINS = ["autometas",
           "redirect",
           "draft",
           "languages",
           "content_types",
           "jinja_helpers"]

""" For Plugins """
