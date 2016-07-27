{% import 'g.tpl' %}
{% include '_css.tpl' %}
{% include '_header.tpl' %}

<h1>
    <span sup-editor-meta ng-model="meta.title" default="{{_('Title')}}"></span>
</h1>

<div sup-query="post" ng-model="query.post">
    <div ng-repeat="post in query.post" sup-editor-open file="post">
      <a href="{{post.url}}">
        <h2>{{post.title}}</h2>
        <img src="{{post.featured_img.src}}" alt="featured_img">
        <div>{{post.author}}</div>
        <time datetime="2016-04-06">{{post.date|date_formatted}}</time>
        <p>{{post.description}}</p>
      </a>
    </div>
</div>

{% include '_footer.tpl' %}