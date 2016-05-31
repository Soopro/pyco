{% import 'g.tpl' %}
{% include '_css.tpl' %}
{% include '_header.tpl' %}

<h1>
    <span sup-editor-meta ng-model="meta.title" default="{{_('Title')}}"></span>
</h1>
<div>
    <span sup-editor-meta ng-model="meta.author" default="{{_('Author')}}"></span>
</div>
<time datetime="2016-04-06">{{meta.date_formatted}}</time>
<div sup-editor-media ng-model="meta.featured_img">
    <img ng-src="{{meta.featured_img.src}}" alt="featured_img">
</div>
<p>
    <span sup-editor-meta ng-model="meta.description" default="{{_('Description text here')}}"></span>
</p>

<div sup-angular-wysiwyg ng-model="content" default="{{_('$_CONTENT')}}">
</div>

<div sup-editor-widget-gallery ng-model="meta.gallery">
    <div ng-repeat="item in meta.gallery">
        <a href="{{item.link}}" target="{{item.target}}" class="{{item.class}}">
            <img ng-src="{{item.src}}">
            <h2>{{item.title}}</h2>
            <p>{{item.caption}}</p>
        </a>
    </div>
</div>

{% include '_footer.tpl' %}