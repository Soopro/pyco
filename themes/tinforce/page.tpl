<!-- Webfonts -->
<link href='{{ theme_url }}/font/webfonts.css' rel='stylesheet' type='text/css'>
<!-- <link href='http://fonts.googleapis.com/css?family=Lato:100,300,400,100italic,300italic,400italic' rel='stylesheet' type='text/css'> -->

<!-- Bootstrap core CSS -->
<link href="{{ theme_url }}/lib/bootstrap/css/bootstrap.min.css" rel="stylesheet" type='text/css'>
<!-- Lightbox CSS -->
<link href="{{ theme_url }}/lib/lightbox/css/lightbox.css" rel="stylesheet" type='text/css'>

<!-- Styles-->
<link href="{{ theme_url }}/css/style.css" rel="stylesheet" type='text/css'>
<link href="{{ theme_url }}/css/{{locale}}.css" rel="stylesheet" type='text/css'>
<div id="wrapper">
	<!-- Header -->
	<header id="header" class="container" unselectable="on">
		<div class="row">
			<div id="language" class="col-md-2 col-sm-2 pull-right">
				<span id="language-switcher" class="language-switcher-btn-disabled">Language</span>
			</div>
			<div id="logo" class="col-md-2 col-sm-2">
				<a href="#" class="logo-graph" fake>Tinforce</a>
			</div>

			<nav id="nav" class="col-md-4 col-sm-4">
				<ul>
					<li><a href="#" fake>Works</a></li>
					<li><a href="#" fake>About</a></li>
				</ul>
			</nav>
		</div>
	</header>
	<!-- #Header -->
	<!-- Tagline -->
	<div class="container">
		<section class="jumbotron">
			<h1 class="title" sup-editor-meta ng-model="file.meta.tagline">Page Tagline</h1>
		</section>
	</div>
	<!-- #Tagline -->
	<!-- Contents -->
	<div class="container">
		<div sup-angular-wysiwyg="sup-editor" ng-model="file.content">
			<h2>This is default content preset</h2>
			<p>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
			<div><img src="{{ theme_url }}/sample_image.png" alt="sample"></div>
			<p>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum</p>
		</div>
	</div>
	<!-- #Contents -->
	<!-- Footer -->
	<footer class="container" unselectable="on">
		<hr>
		<p id="cp">&copy; 2014 Tinforce Digital Studio.</p>
	</footer>
	<!-- #Footer -->
</div>