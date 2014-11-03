/*global CONFIG: true */
/* exported CONFIG */
var THEME_NAME = 'tinforce'
var CONFIG = {
    host: location.protocol+'//'+location.hostname+(location.port ? ':'+location.port: '')+'/',
    editor_params:{ 
		'file':'page',
		'template': 'index',
	},
	site_config:{
		'title':'Site title',
		'description':'Site Descrption here......',
		'copyright':'&copy; 2014 Tinforce Digital Studio.',
		'categories':{
			'cat_slug':'Cat Name',
		},
	},
    theme_config:{
		'alias':THEME_NAME,
    	'templates':{
    		'template':'Template Name',
    	},
    },
};