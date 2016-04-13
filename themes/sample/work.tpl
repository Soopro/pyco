{% import 'g.tpl' %}
{% include '_css.tpl' %}
{% include '_header.tpl' %}

<h1>
    <span sup-editor-meta ng-model="meta.title" default="{{_('Title')}}"></span>
</h1>

<img src="{{meta.featured_img.src}}" alt="featured_img">

<p>
    <span sup-editor-meta ng-model="meta.description" default="{{_('Description text here')}}"></span>
</p>

<div sup-editor-widget-gallery ng-model="meta.gallery">
    <div ng-repeat="item in meta.gallery">
        <a href="{{item.link}}" target="{{item.target}}" class="{{item.class}}">
            <img src="{{item.src}}" alt="gallery_img">
            <h2>{{item.title}}</h2>
            <p>{{item.caption}}</p>
        </a>
    </div>
</div>

<div sup-angular-wysiwyg ng-model="content" default="{{_('$_CONTENT')}}">
</div>

{% include '_footer.tpl' %}