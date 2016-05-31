{% import 'g.tpl' %}
{% include '_css.tpl' %}
{% include '_header.tpl' %}

<h1>
    <span sup-editor-meta ng-model="meta.title" default="{{_('Title')}}"></span>
</h1>
<h2>
    <span sup-editor-meta ng-model="meta.description" default="{{_('Description text here')}}"></span>
</h2>

{% include '_footer.tpl' %}