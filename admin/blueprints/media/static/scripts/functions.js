(function ($) {
  $(document).ready(function() {
    $(".media-uploader").each(function(e){
      var submit_btn = $(this).find("button[type=submit]");
      var previews = $(this).find('.media-previews');
      $(this).find("input[name='files']").change(function(e) {
        var files = (this.files && this.files[0]) ? this.files : null;
        previews.empty();
        if (!files) {
          submit_btn.hide();
          return
        }
        if (files.length > 12) {
          alert('Too many files to upload. (limited to 12)')
          return
        }
        for(var i=0; i < files.length; i++) {
          var reader = new FileReader();
          reader.onloadend = function(e) {
            var pic = document.createElement('IMG');
            $(pic).attr('src', e.target.result);
            previews.append(pic);
          }
          reader.readAsDataURL(files[i]);
          console.log(i);
        }
        submit_btn.show();
      });
    });

  });
})(jQuery);