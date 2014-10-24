/*global CONFIG: true */
/* exported CONFIG */
var CONFIG = {
    host: location.protocol+'//'+location.hostname+(location.port ? ':'+location.port: '')+'/',
    editor_params:{ 
		'file':'about',
		'template': 'page',
	},
	site_config:{
		'locale':'en',
		'base_url':'http://localhost/~redy/pico',
		'theme_url':'http://localhost/~redy/pico/themes/tinforce',
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