{% import 'g.tpl' %}
{% include '_css.tpl' %}
{% include '_header.tpl' %}

<h1>
    <span sup-editor-meta ng-model="meta.title" default="{{_('Title')}}"></span>
</h1>

<div sup-query="product" ng-model="product">
    <div ng-repeat="product in query.product" sup-editor-open file="product">
        <h2>{{product.title}}</h2>

        <div ng-repeat="c in product.collect">{{c.name}} : {{c.value}}</div>

        <a href="#">{{product.button.name}}</a>
    </div>
</div>

{% include '_footer.tpl' %}