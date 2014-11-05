$(document).ready(function() {
//    console.log(window.location.search.substring(1));
//thumbnails scorller
	$("#my-thumbs-list").mThumbnailScroller({
  	  type:"click-20",
 	   theme:"buttons-out"
});
    if($(location).attr('search').substring(1)){
        $('#myCarousel .item')[0].className='item';
        $('#myCarousel .item')[$(location).attr('search').substring(1)].className='item active';
    }
    
    $(".sidebar-menu").click(function(){
        toggle_menu();
    });
    $(".close-btn").click(function(){
	     toggle_menu(true);
    });
    $(".invoke-area").click(function(e){
		if (($(window).width())>768){
	        toggle_menu(true);
		}
		else{
			toggle_menu();
		}
    });
	$("#my-thumbs-list").mThumbnailScroller({
  	  type:"click-20",
 	   theme:"buttons-out"
	});
	
	if($("#slider-footer").length >0){
		var slider_footer = $("#slider-footer .footer")[0];
		$("#slider-footer").hover(function(){
			console.log(slider_footer)
			$(slider_footer).clearQueue()
			$(slider_footer).animate({bottom:'0'},350);
		},function(){
			$(slider_footer).clearQueue()
			$(slider_footer).animate({bottom:'-80px'},350);
		
		});
	}

	// $(".footer").mouseleave();


//     $(document).click(function(e){
// 			//         var container=$(".carousel-inner .container")[0];
// 			//         if($.contains(container,e.target)){
// 			// toggle_menu(false);
// 	        // menu_left_pos = 30;
// // 	        $(".carousel-inner>.active .sidebar-right").hide();
// // 	        menu_opened=!menu_opened
// // 	        $('.sidebar-menu').css( "right", menu_left_pos+"px");
// 			console.log(e.clientX);
// 			console.log(e.target);
// 			if (($(window).width()-e.clientX)>300){
// 		        menu_left_pos = 30;
// 		        if(menu_opened==true){
// 					menu_opened=false;
// 				}
// 		        $(".carousel-inner>.active .sidebar-right").hide();
// 		        $('.sidebar-menu').css( "right", menu_left_pos+"px");
// 			}
// 			//}
//     });
    
	
    var menu_opened = false;
    var menu_left_pos = 30;
    function toggle_menu(force_close){
        if(menu_opened || force_close){
            menu_left_pos = 30;
            $(".carousel-inner>.active .sidebar-right").hide();
        }else{
            $(".carousel-inner>.active .sidebar-right").show();
            menu_left_pos = 300;
        }
        menu_opened=!menu_opened;
        $('.sidebar-menu').css( "right", menu_left_pos+"px");
    }
    
	$('#myCarousel').on('slide.bs.carousel', function () {
        menu_left_pos = 30;
        if(menu_opened==true){
			menu_opened=false;
		}
        $(".carousel-inner>.active .sidebar-right").hide();
        $('.sidebar-menu').css( "right", menu_left_pos+"px");
		
	})
	/*
		function toggle_menu(){
		if($('.carousel-inner>.active .sidebar-right').position().left>0){
			$('.carousel-inner>.active .sidebar-right').hide();
	        $('.carousel-inner>.active .sidebar-menu').css( "right", "30px");			return;
		}else{
			$('.carousel-inner>.active .sidebar-right').show();
	        $('.carousel-inner>.active .sidebar-menu').css( "right", "300px");
		}
	}
	
	// if($('.carousel-inner>.item').attr('class')=='item'){
	// 	$('.carousel-inner>.item .sidebar-right').hide();
	//         $('.carousel-inner>.item .sidebar-menu').css( "right", "30px");
	// }
	*/
	
    $('.navbar').hover(function(){
        $('.navbar-ul').toggle();
    })


});

/*    
    var thumb_width=100;
    if($('.scrollable-indicators .thumb').length>0){
        thumb_width=$('.scrollable-indicators .thumb').width()+2;
    }
    var btn_scroll_width=50;
    if($('.btn-scroll').length>0){
        btn_scroll_width=$('.btn-scroll').width();
    }
    var init_left= $('.scrollable-indicators').position().left;
    var ol_width= $('.scrollable-indicators').width();
    var totlal_width=$('.scrollable-indicators .thumb').length*thumb_width;
    var limit=totlal_width-ol_width;
    var win_init= $(window).width();
    console.log('i_l: '+init_left);
    $(window).resize(function(){
        ol_width= $('.scrollable-indicators').width();
        var old_left= init_left;
        init_left= $('.scrollable-indicators').parent().width()*.5;
        var changed_left=init_left-old_left;
        limit=totlal_width-ol_width;
        var win_now= $(window).width();
        win_init=win_now;
        if(win_now>win_init){
            if(init_left<old_left){
                var now_left = $('.scrollable-indicators').position().left-init_left;
                var move_to=now_left-thumb_width;
                if(move_to < -limit){
                    move_to = -limit;
                }
                $('.scrollable-indicators').stop().animate({
                    'left':move_to+init_left+'px',
                },200);
                
            }else{
                var now_left = $('.scrollable-indicators').position().left-init_left;
                var move_to=now_left+thumb_width;
                if(move_to > 0){
                    move_to = 0;
                }
        
                $('.scrollable-indicators').stop().animate({
                    'left':move_to+init_left+'px',
                },200);
            }
        }
        
//        $('.scrollable-indicators').position({'left':changed_left*2+win_init+'px'});
        console.log('o_l: '+old_left);
    });
    //+btn_scroll_width*2;
    
    if(limit<thumb_width){
        limit=0;
    }
    $(".btn-scroll-right").click(function () {
        var now_left = $('.scrollable-indicators').position().left-init_left;//?
        var move_to=now_left-thumb_width;
        if(move_to < -limit){
            move_to = -limit;
        }
        $('.scrollable-indicators').stop().animate({
            'left':move_to+init_left+'px',
        },200);
    });
    $(".btn-scroll-left").click(function() {
        var now_left = $('.scrollable-indicators').position().left-init_left;
        var move_to=now_left+thumb_width;
        if(move_to > 0){
            move_to = 0;
        }

        $('.scrollable-indicators').stop().animate({
            'left':move_to+init_left+'px',
        },200);
    });

});
*/    



    