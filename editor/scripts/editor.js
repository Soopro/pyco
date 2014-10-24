/* global supMockEditor: true */
var supMockEditor = angular.module('supMockEditor', [
    'ngRoute',
    'ngResource',
    'ngCookies',
    'ngSanitize',
    'supAngularWysiwyg',
]);
supMockEditor.constant('Config', {
    host:CONFIG.host,
	site_config: CONFIG.site_config,
	theme_config: CONFIG.theme_config,
	editor_params:CONFIG.editor_params,
});

/* Route */
supMockEditor.config(['$routeProvider',
    function ($routeProvider) {
        'use strict';
        $routeProvider.
            when('/', {
                templateUrl: 'views/station.html',
                controller: 'workStationCtrl'
            });
    }]);

/* Service */
supMockEditor.factory('EditorTemplate', ['$resource', 'Config',
    function ($resource, Config) {
        'use strict';
        return $resource(Config.tpl, {
        }, {
        });
    }]);


// Flash Message
supMockEditor.service('FlashMsg', ['$rootScope',
    function ($rootScope) {
        this.show = function (msg, isError) {
            $rootScope.flashMsg = msg;
            $rootScope.flashError = isError;
        };
        this.hide = function () {
            $rootScope.flashMsg = false;
        };
    }]);

/* Directive */
supMockEditor.directive('editorCanvas', function ($http, $compile, EditorTemplate, Config) {
    'use strict';
    return {
        restrict: 'EA',
        scope: {
            'template': '@',
            'file': '=',
            'config':'=',
            'app': '@',
            'type': '@'
        },
        compile: function () {
            return function (scope, element) {
                scope.now = new Date().getTime();
				
				var tpl_url=Config.site_config.theme_url+'/'+scope.template+'.tpl';
				$http.get(tpl_url).success(function(data, status, headers, config) {

					data=replace_template_tag(data,Config.site_config);
	
                    element.html(data);
                    var A = element[0].querySelectorAll('a[fake]');

                    for (var i = 0; i < A.length; i++) {
                        A[i].addEventListener('click', function (e) {
                            e.preventDefault();
                            return false;
                        });
                    }
                    $compile(element.contents())(scope);
				});
            };
        }
    };
});

supMockEditor.directive('supEditorMeta', function () {
      return {
          restrict: 'A', // only activate on element attribute
          require: '?ngModel', // get a hold of NgModelController
          link: function (scope, element, attrs, ngModel) {
              if (!ngModel) return; // do nothing if no ng-model
              element[0].setAttribute('contenteditable', true);
              // Specify how UI should be updated
			  
              ngModel.$render = function () {
				  if(ngModel.$viewValue){
                  	element.html(ngModel.$viewValue);
				  }
              };

              // Listen for change events to enable binding
              element.on('blur keyup change', function () {
                  scope.$apply(readViewText);
              });

              // No need to initialize, AngularJS will initialize the text based on ng-model attribute

              // Write data to the model
              function readViewText() {
                  var html = element.html();
                  // When we clear the content editable the browser leaves a <br> behind
                  // If strip-br attribute is provided then we strip this out
                  if (attrs.stripBr && html == '<br>') {
                      html = '';
                  }
                  ngModel.$setViewValue(html);
              }
          }
      };
  });
  supMockEditor.directive('supEditorWidget', function ($rootScope) {
        return {
            restrict: 'A',
            require: '?ngModel', // get a hold of NgModelController
            link: function (scope, element, attrs, ngModel) {
                if (!ngModel) return; // do nothing if no ng-model
                element[0].addEventListener('click', call_update);
                function call_update(){
                    switch(attrs.supEditorWidget){
                        case 'media':
                            $rootScope.$emit('widget.update_media', scope);
                        break;
                        case 'script':
                            $rootScope.$emit('widget.update_script', scope);
                        break;
                    }
                };
                scope.update = function (data){
                    ngModel.$setViewValue(data);
                    ngModel.$render();
                };
                ngModel.$render = function () {
					if(ngModel.$viewValue){
	                    switch(attrs.supEditorWidget){
	                        case 'media':
	                            element[0].src=ngModel.$viewValue;
	                        break;
	                        case 'script':
	                            element.html(ngModel.$viewValue);
	                        break;
	                    }
					}
                };
                scope.$on('$destroy', function() {
                    element[0].removeEventListener('click', call_update);
                });
            }
        };
    });
//for mock editor only
var re_base_url=/{{\s*base_url\s*}}/gi;
var re_theme_url=/{{\s*theme_url\s*}}/gi;
var re_locale=/{{\s*locale\s*}}/gi;
var re_site_description=/{{\s*site_description\s*}}/gi;
var re_site_keywords=/{{\s*site_keywords\s*}}/gi;
var re_site_title=/{{\s*site_title\s*}}/gi;
var re_site_license=/{{\s*site_license\s*}}/gi;
var re_site_copyright=/{{\s*site_copyright\s*}}/gi;
var re_site_contacts=/{{\s*site_contacts\s*}}/gi;

function replace_template_tag(data,params){
	data=data.replace(re_base_url,params.base_url);
	data=data.replace(re_theme_url,params.theme_url);
	data=data.replace(re_locale,params.locale);
	data=data.replace(re_site_description,params.site_description);
	data=data.replace(re_site_keywords,params.site_keywords);
	data=data.replace(re_site_title,params.site_title);
	data=data.replace(re_site_license,params.site_license);
	data=data.replace(re_site_copyright,params.site_copyright);
	data=data.replace(re_site_contacts,params.site_contacts);
	
	return data;
}