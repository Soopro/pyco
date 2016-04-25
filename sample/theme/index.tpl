{% import 'g.tpl' %}
{% include '_css.tpl' %}
{% include '_header.tpl' %}

<div id="myCarousel" class="carousel slide" data-ride="carousel" style="height: 200px;">
      <div class="carousel-inner" role="listbox" sup-editor-widget-gallery ng-model="meta.carousels">
        <div class="item">
          <a href="{{item.link}}"><img ng-src="{{item.src}}"></a>
        </div>
      </div>
</div>

{% include "_footer.tpl" %}