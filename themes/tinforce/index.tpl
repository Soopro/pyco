<!-- Webfonts -->
<link href='{{ theme_url }}/font/webfonts.css' rel='stylesheet' type='text/css'>
<!-- <link href='http://fonts.googleapis.com/css?family=Lato:100,300,400,100italic,300italic,400italic' rel='stylesheet' type='text/css'> -->

<!-- Bootstrap core CSS -->
<link href="{{ theme_url }}/lib/bootstrap/css/bootstrap.min.css" rel="stylesheet">
<!-- Lightbox CSS -->
<link href="{{ theme_url }}/lib/lightbox/css/lightbox.css" rel="stylesheet">

<!-- Styles-->
<link href="{{ theme_url }}/css/style.css" rel="stylesheet" type='text/css'>
<link href="{{ theme_url }}/css/{{locale}}.css" rel="stylesheet" type='text/css'>
<div id="wrapper">
	<!-- Header -->
	<header id="header" class="container">
		<div class="row">
			<div id="language" class="col-md-2 col-sm-2 pull-right">
				<span id="language-switcher" class="language-switcher-btn-disabled">Language</span>
			</div>
			<div id="logo" class="col-md-2 col-sm-2">
				<a href="#" class="logo-graph">Tinforce</a>
			</div>

			<nav id="nav" class="col-md-4 col-sm-4">
				<ul>
					<li><a href="#">Works</a></li>
					<li><a href="#">About</a></li>
				</ul>
			</nav>
		</div>
	</header>
	<!-- #Header -->
	<!-- Tagline -->
	<div class="container" ng-init="file.meta.tagline = file.meta.tagline || 'PERFECT ONLINE SOLUTIONS<br>FOR MICRO BUSINESS.'">
		<section class="jumbotron">
			<h1 sup-editor-meta ng-model="file.meta.tagline">PERFECT ONLINE SOLUTIONS<br>FOR MICRO BUSINESS.</h1>
		</section>
	</div>
	<!-- #Tagline -->
	<!-- Contents -->
	<div class="container">
		
	</div>
	<!-- #Contents -->
	<!-- Footer -->
	<footer class="container">
		<hr>
		<p id="cp">&copy; 2014 Tinforce Digital Studio.</p>
	</footer>
	<!-- #Footer -->
</div>