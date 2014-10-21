/**
TinForce Javascript
http://www.tinforce.com

Author:   redy
**/

//fix old browser no console
if (!window.console) {
	window["console"] = {log: function(){}};
}

var item_limit=12;
var item_count=0;
var item_step=4;

$(document).ready(function () {
	//Language Switcher
	$('#language-switcher').click(function() {
		$($(this).attr('href')).toggle(200);
		return false;
	});
	
	//Pagination
	if($('.works-list').length>0){
		$('.works-list').each(function(){
			var $figure=$(this).children('figure');
			$figure.each(function(){
				if(item_count<item_limit){
					$(this).show();
					item_count++;
				}
			});
			
			var $btn_more=$(this).parent().find('.btn-more');
			if(item_count<$figure.length){
			
				if($btn_more.length>0){
					$btn_more.show();
					$btn_more.click(function(){
						
						var tmp_last=item_count;
						
						item_limit=tmp_last+item_step;
						item_limit=item_limit>$figure.length?$figure.length:item_limit;

						item_count=0;

						$figure.each(function(){
							if(item_count<item_limit){
								$(this).show();
								item_count++;
							}
							console.log(item_count);
						});
						
						if(item_count>=$figure.length){
							$btn_more.hide();
						}
						return false;
					});
				}
				
			}
		});
	}
	
	//Lightbox
	$('.lightbox-gallery').each(function(){
		$(this).attr('data-lightbox','lightbox-gallery');	
	});
	
	function resizeLightboxOverlay(){
		$("#lightboxOverlay").width($(document).width());
	}
	$(window).resize(function(){
		resizeLightboxOverlay();
	});
	
	
	//External links for _blank
	$('a[rel="external"]').each(function(){
		if(!$(this).data('target')){
			$(this).attr('target','_blank');
		}else{
			$(this).attr('target',$(this).data('target'));
		}
	});
});