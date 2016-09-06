{% import 'g.tpl' %}
{% include '_css.tpl' %}
{% include '_header.tpl' %}

<h1>
    <span sup-editor-meta ng-model="meta.title" default="{{_('Title')}}"></span>
</h1>

<div sup-query="works" ng-model="query.works">
    <div class="col-md-3" ng-repeat="works in query.works" sup-editor-open file="works">
        <a href="{{work.url}}">
            <img src="{{work.featured_img.src}}">
            <h1>{{work.title}}</h1>
        </a>
    </div>
</div>

<div>
<a href="#" class="btn btn-default btn-md">{{_('Prev')}}</a>
<a href="#" class="btn btn-default btn-md">{{_('Next')}}</a>
</div>

{% include '_footer.tpl' %}