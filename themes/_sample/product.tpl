{% import 'g.tpl' %}
{% include '_css.tpl' %}
{% include '_header.tpl' %}

<div>
    <h2>
        <span sup-editor-meta ng-model="meta.title" defualt="{{_('Title')}}"></span>
    </h2>

    <div sup-editor-widget-collect ng-model="meta.collect">
        <div ng-repeat="c in meta.collect">{{c.name}} : {{c.value}}</div>
    </div>

    <div sup-editor-widget-button ng-model="meta.button">
        <a href="#">{{meta.button.name}}</a>
    </div>
</div>

{% include '_footer.tpl' %}