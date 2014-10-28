/* Controller */
supMockEditor.controller('workStationCtrl', [
    '$scope', '$rootScope','$timeout','$route','$cookieStore',
    'SawEditor','FlashMsg','Config',
    function ($scope, $rootScope, $timeout, $route, $cookieStore, SawEditor, FlashMsg,Config) {
        'use strict';
        
        $scope.file = {
            meta: {
                title:'',
                template:'',
                draft:true,
                markdown:false,
                order:'',
            }, 
            content: '', 
            slug:'',
            uri:'',
        };
        
        var params=Config.editor_params;
		
        $scope.file.slug = params.file;
        $scope.file.meta.template = params.template;
		$scope.file.meta.picture = '#';
		$scope.appType = 'ws';
        $scope.appSlug = 'test';
        $scope.appInfo = {};
        $scope.contentType = 'test_content_type';
        $scope.isNewFile = true;
        $scope.templates=[];
        $scope.categories=[];
        $scope.markdown=false;
        $scope.draft=false;
        $scope.settings={};
        $scope.editor_on_blur=true;
		
        loadTemplate();
        
        //load theme config
        function loadTemplate(){
            $scope.settings=Config.site_config;
            var theme_config=Config.theme_config;
            
            angular.forEach(theme_config.templates, function (name, key) {
               $scope.templates.push({"slug":key,"name":name});
            });
            angular.forEach($scope.settings.categories, function (name, key) {
               $scope.categories.push({"slug":key,"name":name});
            });
        };
        
        //set org html to content if newfile while editor is loaded.
        var clean_complete = $rootScope.$on('editor.complete', function (e, saw, org_html) {
            if ($scope.isNewFile) {
                $scope.file.meta.title = $scope.file.slug;
                $scope.file.content = org_html;
            }
        });
        
        //manage image
        var current_editor;
        var clean_insert_image = $rootScope.$on('editor.insert_image', function (e, saw) {
            current_editor = saw;
            console.log('------------------------------------');
			console.log('Insert image!!');
			console.log('------------------------------------');
        });
        var clean_replace_image = $rootScope.$on('editor.replace_image', function (e, saw) {
            current_editor = saw;
            console.log('------------------------------------');
			console.log('Replace image!!');
			console.log('------------------------------------');
        });
        var clean_widget_update_media = $rootScope.$on('widget.update_media', function (e, widget) {
            console.log('------------------------------------');
			console.log('Update Media Widget!!');
			console.log('------------------------------------');
        });
        
        //set current editor while switch editor.
        var clean_focus = $rootScope.$on('editor.focus', function (e, saw) {
            current_editor = saw;
            $scope.editor_on_blur=false;
        });
        //remove current editor.
        var clean_blur = $rootScope.$on('editor.blur', function (e, saw) {
            $scope.editor_on_blur=true;
        });
        
        //set html area for current editor.
        $scope.showhtml=false;
        var clean_html_open = $rootScope.$on('editor.html.open', function (e) {
            $scope.showhtml=true;
        });
        var clean_html_close = $rootScope.$on('editor.html.close', function (e) {
            $scope.showhtml=false;
        });

        //clear $on
        $scope.$on('$destroy', function() {
            clean_replace_image();
            clean_insert_image();
            clean_complete();
            clean_focus();
            clean_blur();
            clean_html_open();
            clean_html_close();
            clean_widget_update_media();
        });
        
        /* toggle UI */
        $scope.show_toolbar = true;
        $scope.show_property = false;
        $scope.show_advopts = false;
        
        $scope.toggleProperty = function () {
            $scope.show_property = !$scope.show_property;
        };
        
        $scope.toggleToolbar = function () {
            $scope.show_toolbar = !$scope.show_toolbar;
        };

        $scope.toggleMarkdown = function () {
            $scope.markdown = !$scope.markdown;
        };
        
        $scope.toggleAdv = function () {
            $scope.show_advopts = !$scope.show_advopts;
        };
        
        
        /* Operation */
        $scope.get_today = function (){
            var today = new Date();
            var dd = today.getDate();
            var mm = today.getMonth()+1; //January is 0!
            var yyyy = today.getFullYear();
            if(dd<10) {
                dd='0'+dd;
            } 
            
            if(mm<10) {
                mm='0'+mm;
            }
            today = yyyy+'/'+mm+'/'+dd;
            
            $scope.file.meta.date = today;
        };
   
        $scope.get_author = function (){
           
        };
        
        $scope.get_thumb = function (){
            
        };
        
        $scope.close = function () {
            window.close();
        };
        
        $scope.save = function () {
            formatMeta(true);
            $scope.show_property = false;
            var content=$scope.file.content;
            if(!$scope.markdown){
                content=content.replace(/\s{2,}/g, ' ').trim();
            }
            if (!content){
                content=' ';
            }

            console.log('------------------------------------');
			console.log('Meta:');
			console.log($scope.file.meta);
			console.log('Content:');
			console.log(content);
			console.log('------------------------------------');
        };

        $scope.delete = function () {
            EditorSingleFile.delete({
                'apptype': $scope.appType,
                'slug': $scope.appSlug,
                'content_type_slug': $scope.contentType,
                'file_slug': $scope.file.slug
            }, function () {
                window.close();
            });
        };
        
        function formatMeta(is_save){
            if (!$scope.file.meta.title){
                $scope.file.meta.title = $scope.file.slug;
            }
            if(!$scope.file.meta.template){
                $scope.file.meta.template=$scope.contentType;
            }

            if(!$scope.file.meta.order || $scope.file.meta.order=='None'){
                $scope.file.meta.order='';
            }else{
                $scope.file.meta.order=parseInt($scope.file.meta.order);
            }
            if (!$scope.file.meta.date){
                $scope.get_today();
            }
            
            if (!$scope.file.meta.author){
                $scope.get_author();
            }
            
            
            if(!is_save){
                if($scope.file.meta.draft=='True'){
                    $scope.file.meta.draft=true;
                }else{
                    $scope.file.meta.draft=false;
                }
                if($scope.file.meta.markdown=='True'){
                    $scope.markdown=true;
                }else{
                    $scope.markdown=false;
                }
            }else{
                if(!$scope.file.meta.draft && is_save){
                    $scope.file.meta.draft='';
                }
                $scope.file.meta.markdown=$scope.markdown;
            }
            
        }
        
        function removeParam(key, sourceURL) {
            var rtn = sourceURL.split("?")[0],
                param,
                params_arr = [],
                queryString = (sourceURL.indexOf("?") !== -1) ? sourceURL.split("?")[1] : "";
            if (queryString !== "") {
                params_arr = queryString.split("&");
                for (var i = params_arr.length - 1; i >= 0; i -= 1) {
                    param = params_arr[i].split("=")[0];
                    if (param === key) {
                        params_arr.splice(i, 1);
                    }
                }
                rtn = rtn + "?" + params_arr.join("&");
            }
            return rtn;
        }
        
        function setParam(paramName, paramValue, sourceURL){
            var url = sourceURL;
            if (url.indexOf(paramName + "=") >= 0){
                var prefix = url.substring(0, url.indexOf(paramName));
                var suffix = url.substring(url.indexOf(paramName));
                suffix = suffix.substring(suffix.indexOf("=") + 1);
                suffix = (suffix.indexOf("&") >= 0) ? suffix.substring(suffix.indexOf("&")) : "";
                url = prefix + paramName + "=" + paramValue + suffix;
            }else{
                if (url.indexOf("?") < 0){
                    url += "?" + paramName + "=" + paramValue;
                }else{
                    url += "&" + paramName + "=" + paramValue;
                }
            }
            return url;
        }
        
        /* init */
        formatMeta();
    }]);