function shareFriend() {
	WeixinJSBridge.invoke('sendAppMessage',{
							"appid": appid,
							"img_url": imgUrl,
							"img_width": "",
							"img_height": "",
							"link": lineLink,
							"desc": descContent,
							"title": shareTitle
							}, function(res) {
							//_report('send_msg', res.err_msg);
							})
}
function shareTimeline() {
    WeixinJSBridge.invoke('shareTimeline',{
                            "img_url": imgUrl,
                            "img_width": "",
                            "img_height": "",
                            "link": lineLink,
                            "desc": descContent,
                            "title": shareTitle
                            }, function(res) {
                            //_report('timeline', res.err_msg);
                            });
}
function shareWeibo() {
    WeixinJSBridge.invoke('shareWeibo',{
                            "content": descContent,
                            "url": lineLink,
                            }, function(res) {
                            //_report('weibo', res.err_msg);
                            });
}
document.addEventListener('WeixinJSBridgeReady', function onBridgeReady() {

        
        WeixinJSBridge.on('menu:share:appmessage', function(argv){
            shareFriend();
            });

        
        WeixinJSBridge.on('menu:share:timeline', function(argv){
            shareTimeline();
            });

        
        WeixinJSBridge.on('menu:share:weibo', function(argv){
            shareWeibo();
            });
        }, false);