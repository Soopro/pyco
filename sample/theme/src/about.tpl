{% import 'g.tpl' %}
{% include '_css.tpl' %}
{% include '_header.tpl' %}

<h1>
    <span sup-editor-meta ng-model="meta.title" default="{{_('Title')}}"></span>
</h1>
<p>
    <span sup-editor-meta ng-model="meta.description" default="{{_('Description text here')}}"></span>
</p>

<div sup-editor-widget-gallery ng-model="meta.teams">
    <div class="col-sm-6 col-md-4" ng-repeat="item in meta.teams">
      <img src="{{item.src}}">
      <div>
        <h3>{{item.title}}</h3>
        <p>{{item.caption}}</p>
      </div>
    </div>
</div>

{% include '_footer.tpl' %}