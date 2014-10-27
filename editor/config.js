/*global CONFIG: true */
/* exported CONFIG */
var CONFIG = {
    host: location.protocol+'//'+location.hostname+(location.port ? ':'+location.port: '')+'/',
    editor_params:{ 
		'file':'test',
		'template': 'works',
	},
	site_config:{
		'locale':'en',
		'base_url':'http://localhost:5000',
		'theme_url':'http://localhost:5000/static',
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