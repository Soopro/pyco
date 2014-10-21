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
	<div class="container" ng-init="file.meta.tagline = file.meta.tagline || 'Works'">
		<section class="jumbotron">
			<h1 class="title" sup-editor-meta ng-model="file.meta.tagline">Works</h1>
			<a href="#" class="btn-list" fake></a>
		</section>
	</div>
	<!-- #Tagline -->
	<!-- Contents -->
	<div class="container">
		<section class="row">
			<div class="col-md-4 col-sm-4 pull-right">
				<article>
					<header ng-init="file.meta.title = file.meta.title || 'Works title here'">
						<h5 sup-editor-meta ng-model="file.meta.title">Works title here</h5>
					</header>
					<div sup-editor-meta ng-init="file.meta.brief = file.meta.brief || 'Works brief is here. It is in a paragraph.'" ng-model="file.meta.brief">
						Works brief is here. It is in a paragraph.
					</div>
					<ul class="metadata">
						<li ng-init="file.meta.date = file.meta.date || '1989/12/30'">
							<p sup-editor-meta ng-model="file.meta.date">1989/12/30</p>
						</li>
						<li ng-init="file.meta.task = file.meta.task || 'Task Status'">
							<p sup-editor-meta ng-model="file.meta.task">Task status</p>
						</li>
						<li ng-init="file.meta.link = file.meta.link || 'http://type.works.link.here'">
							<p><a rel="external" href="#" sup-editor-meta class="fake" ng-model="file.meta.link">http://type.works.link.here</a></p>
						</li>
					</ul>
				</article>
			</div>
			<div class="col-md-8 col-sm-8 pull-left">
				<aside>
					<div sup-angular-wysiwyg="sup-editor" ng-model="file.content">
						<p>
							<a href="{{ theme_url }}/sample_img.png" title="screenshot" class="lightbox-gallery">
								<img src="{{ theme_url }}/sample_image.png" alt="project screenshot.">
							</a>
						</p>
						<p>
							<a href="{{ theme_url }}/sample_img.png" title="screenshot" class="lightbox-gallery">
								<img src="{{ theme_url }}/sample_image.png" alt="project screenshot.">
							</a>
						</p>
						<p>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
						<p>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
					</div>
				</aside>
			</div>
		</section>
	</div>
	<!-- #Contents -->
	<!-- Footer -->
	<footer class="container">
		<hr>
		<p id="cp">&copy; 2014 Tinforce Digital Studio.</p>
	</footer>
	<!-- #Footer -->
</div>