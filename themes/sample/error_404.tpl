{% import 'g.tpl' %}
{% include '_css.tpl' %}
{% include '_header.tpl' %}

<h1>{{meta.title or _('Title')}}</h1>
<h2>{{meta.description or _('Description text here')}}</h2>

{% include '_footer.tpl' %}