{% import 'g.tpl' %}
{% include '_css.tpl' %}
{% include '_header.tpl' %}

<h1>
    <span sup-editor-meta ng-model="meta.title" default="{{_('Title')}}"></span>    
</h1>

<div sup-angular-wysiwyg ng-model="content" default="{{_('$_CONTENT')}}">
</div>

{% include '_footer.tpl' %}