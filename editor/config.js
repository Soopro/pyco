/*global CONFIG: true */
/* exported CONFIG */
var CONFIG = {
    host: location.protocol+'//'+location.hostname+(location.port ? ':'+location.port: '')+'/',
    editor_params:{ 
		'file':'test',
		'template': 'index',
	},
	site_config:{
		'locale':'en',
		'base_url':'http://127.0.0.1:5000',
		'theme_url':'http://127.0.0.1:5000/static',
        'theme_tpl_url':'http://127.0.0.1:5000/editor/tpl',
		'site_description':'Site Descrption here......',
		'site_copyright':'&copy; 2014 tinforce.com',
		'categories':{
			'cat_slug':'Cat Name',
		},
	},
    theme_config:{
    	'templates':{
    		'template':'Template Name',
    	},
    },
};