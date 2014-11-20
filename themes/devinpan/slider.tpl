<div style="position:relative; height:800px">

<!-- Bootstrap -->
<link href="{{theme_url}}css/bootstrap.min.css" rel="stylesheet">
<!--mThumbnail scroller css-->
<link rel="stylesheet" href="{{theme_url}}css/jquery.mThumbnailScroller.css">
<!--custom CSS-->
<link href='{{theme_url}}css/slider.css' rel='stylesheet' >
<link href='{{theme_url}}css/font-awesome.css' rel='stylesheet' >

    <!--navbar-->
	<nav class="navbar navbar-inverse slider-navbar" role="navigation">
	  <div class="container-fluid">
	    <!-- Brand and toggle get grouped for better mobile display -->
	    <div class="navbar-header">
	      <button type="button" class="navbar-toggle collapsed sm-navbtn" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1">
	        <i class="fa fa-angle-double-down fa-2x"></i>
	      </button>
	      <a class="navbar-brand" href="#">{{site_meta.title}}</a>
	    </div>

	    <!-- Collect the nav links, forms, and other content for toggling -->
	    <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
	      <ul class="nav navbar-nav">
		<li><a href="{{item.url}}" class="text-uppercase">INDEX</a></li>
        <li><a href="{{item.url}}" class="text-uppercase">GALLERY</a></li>
		<li><a href="{{item.url}}" class="text-uppercase">CONTACT</a></li>
	      </ul>
	    </div><!-- /.navbar-collapse -->
	  </div><!-- /.container-fluid -->
	</nav>
	

    <!--#navbar-->
	    <div class="lg-custom-navbar">
	        <div class="navbar-logo" href="">
	            <img class="navbar-img" src="{{theme_url}}img/logo.png" alt="" />
			</div>
		      <ul class="nav navbar-nav">
			<li><a href="{{item.url}}" class="text-uppercase" fake-link>INDEX</a></li>
	        <li><a href="{{item.url}}" class="text-uppercase" fake-link>GALLERY</a></li>
			<li><a href="{{item.url}}" class="text-uppercase" fake-link>CONTACT</a></li>
		      </ul>
			  </div>
	<!--        </div>-->
	
    <!--sidebar menu-->
    <div class="pull-right sidebar-menu" style="right:300px">
        <a class="menu-align-right">
            <i class="fa fa-info fa-2x"></i>
        </a>
    </div>
    <!--#sidebar menu-->
   <div id="myCarousel" class="carousel carousel-fullscreen slide" data-ride="carousel">
       <!--carousel item-->
       <div class="carousel-inner">
		   
           <div class="item active">
               <div class="carousel-imgbox invoke-area" style="background: url('{{theme_url}}img/background.jpg') ;" ></div>
               <!--right-menu-->
               <div class="container" >
                       <div class="row-offcanvas-right sidebar-right" style="display:block;">
						   <span class="glyphicon glyphicon-remove close-btn pull-right"></span>
                           <h3 sup-editor-meta ng-model="file.meta.title">Sample Title</h3>
                           <a class="pull-left" href="javascript:"><img src="{{theme_url}}img/icon_clock.png" alt="" /></a>
                           <h5 sup-editor-meta ng-model="file.meta.date"></h5>
                           <a class="pull-left" href="javascript:"><img src="{{theme_url}}img/icon_location.png" alt="" /></a>
                           <h5 sup-editor-meta ng-model="file.meta.location"> HangZhou </h5>
                           <br />
                           <p class="pull-right"sup-editor-meta ng-model="file.meta.content">The top CSS property specifies part of the position of positioned elements. It has no effect on non-positioned elements.

For absolutely positioned elements (those with position: absolute or position: fixed), it specifies the distance between the top margin edge of the element and the top edge of its containing block.
                           </p>
                           <a class="pull-right" href="javascript:"><img src="{{theme_url}}img/icon_like.png" alt="" /></a>
                           <a class="pull-right" href="javascript:"><img src="{{theme_url}}img/icon_share.png" alt="" /></a>
                           
                       </div>
               </div>
           </div>
	</div>
	
   </div>
   </div>
   <a class="left carousel-control" href="#myCarousel" role="button" data-slide="prev">
       <span class="glyphicon glyphicon-chevron-left"></span>
   </a>
   <a class="right carousel-control" href="#myCarousel" role="button" data-slide="next">
       <span class="glyphicon glyphicon-chevron-right"></span>
   </a>
</div>