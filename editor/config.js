/*global CONFIG: true */
/* exported CONFIG */
var THEME_NAME = 'tinforce'
var CONFIG = {
    host: location.protocol+'//'+location.hostname+(location.port ? ':'+location.port: '')+'/',
    editor_params:{ 
		'file':'page',
		'template': 'page',
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
	mock_query:{
		query_sample:[
			{'alias':'test'},
			{'title':'Title Test'},
			{'description':'This is not very long decrtiption for test'},
			{'date':12323123213}, //timestamp
			{'updated':12323123213}, //timestamp
		]
	}
};