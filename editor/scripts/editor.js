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
supMockEditor.directive('editorCanvas', function ($http, $compile,  Config) {
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
				var tpl_url='/editor/tpl/'+scope.template;
				scope.config = {'site_meta':Config.site_config,'theme_meta':Config.theme_config};
				scope.site_meta = scope.config.site_meta;
				scope.theme_meta = scope.config.theme_meta;
				
				$http.get(tpl_url).success(function(data, status, headers, config) {
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
			  	console.log('---> Editor Meta box');
          }
      };
  });
supEditor.directive('supEditorWidget', function ($rootScope) {
      return {
          restrict: 'A',
          require: '?ngModel', // get a hold of NgModelController
          link: function (scope, element, attrs, ngModel) {
              if (!ngModel) return; // do nothing if no ng-model
              element[0].addEventListener('click', call_update);
            
              function call_update(e){
                  if(e.target==element[0]){
                      switch(attrs.supEditorWidget){
                          case 'media':
								console.log('------------------------------------');
								console.log('Call Media Widget!!');
								console.log('------------------------------------');
                          break;
                          case 'script':
	  				            console.log('------------------------------------');
	  				  			console.log('Call Script Widget!!');
	  				  			console.log('------------------------------------');
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