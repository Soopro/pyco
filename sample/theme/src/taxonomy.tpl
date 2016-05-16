{% import 'g.tpl' %}
{% include '_css.tpl' %}
{% include '_header.tpl' %}

<div class="bg {{meta.background.class}}" style="{{meta.background.style || site_meta.bg.style}}" sup-editor-widget-bg ng-model="meta.background">
  <h1>
    <span sup-editor-meta ng-model="meta.title" default="{{_('Title')}}"></span>
  </h1>
  <p>
    <span sup-editor-meta ng-model="meta.description" default="{{_('Description text here')}}"></span>
  </p>
  <p sup-editor-widget-button ng-model="meta.button">
    <a href="#">
      {{meta.button.name}}
    </a>
  </p>
</div>

<ul ng-if="tax.category && tax.category.terms.length > 0">
  <li ng-repeat="term in tax.category.terms">
    <a href="/terms?tax={{term.taxonomy}}&term={{term.slug}}">{{term.title}}</a>
  </li>
</ul>

{% include '_footer.tpl' %}