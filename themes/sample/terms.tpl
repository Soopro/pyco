{% import 'g.tpl' %}
{% include '_css.tpl' %}
{% include '_header.tpl' %}

<div class="container" sup-query="work" ng-model="query.work">
    {% set _cat = work.taxonomy.category or [] %}
    {% set arg_term = request.args.term %}
    <div class="col-md-3" ng-if="arg_term in _cat"
     ng-repeat="work in query.work"
     sup-editor-open
     file="work">
        <img src="{{work.featured_img.src}}" alt="img">
        <h1>{{work.title}}</h1>
    </div>
</div>

{% include '_footer.tpl' %}