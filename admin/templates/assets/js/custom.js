/**
 *
 * You can write your JS code here, DO NOT touch the default style file
 * because it will make it harder for you to update.
 *
 */

"use strict";

$(document).ready(function() {

  /* Alert */
  $('.alert-dismissible').on('click', function(e){
    $(this).find('button.close').click();
  });

  /* Uploader */

  $('.file-uploader').each(function(){
    var uploader = $(this);
    uploader.find('input[name="file"]').on('change', function(e){
      var target = e.currentTarget || e.target;
      if (target && target.value) {
        uploader.submit();
      }
    });
    uploader.find('input[name="files"][multiple]').on('change', function(e){
      var target = e.currentTarget || e.target;
      if (target && target.value) {
        var limit = parseInt($(this).attr('maxlength')) || 60;
        if (this.files.length <= limit) {
          uploader.submit();
        } else {
          alert($(this).attr('maxlength-error'));
        }
      }
    });
  });

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