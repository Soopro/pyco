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
		<section class="jumbotron" ng-init="file.meta.title = file.meta.title || 'Error 404'">
			<h1 class="title" sup-editor-meta ng-model="file.meta.title">Error 404</h1>
		</section>
	</div>
	<!-- #Tagline -->
	<!-- Contents -->
	<div class="container">
		<article>
			<div sup-angular-wysiwyg="sup-editor" name="sup-editor" order="0" toolbar="sup-editor-toolbar" components="sup-editor-components" textarea="sup-editor-textarea" contenteditable="true" ng-model="file.content">
				<p>Woops. Looks like this page doesn't exist.</p>
			</div>
		</article>
	</div>
	<!-- #Contents -->
	<!-- Footer -->
	<footer class="container" unselectable="on">
		<hr>
		<p id="cp">&copy; 2014 Tinforce Digital Studio.</p>
	</footer>
	<!-- #Footer -->
</div>