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

  // $(".media-uploader").each(function(e){
  //   var submit_btn = $(this).find("button[type=submit]");
  //   var previews = $(this).find('.media-previews');
  //   $(this).find("input[name='files']").change(function(e) {
  //     var files = (this.files && this.files[0]) ? this.files : null;
  //     previews.empty();
  //     if (!files) {
  //       submit_btn.hide();
  //       return
  //     }
  //     if (files.length > 12) {
  //       alert('Too many files to upload. (limited to 12)')
  //       return
  //     }
  //     for(var i=0; i < files.length; i++) {
  //       var reader = new FileReader();
  //       reader.onloadend = function(e) {
  //         var pic = document.createElement('IMG');
  //         $(pic).attr('src', e.target.result);
  //         previews.append(pic);
  //       }
  //       reader.readAsDataURL(files[i]);
  //       console.log(i);
  //     }
  //     submit_btn.show();
  //   });
  // });

  /* Editting */
  $('form.editing').on('keyup keypress', function(e) {
    var keyCode = e.keyCode || e.which;
    if (keyCode === 13) {
      e.preventDefault();
      return false;
    }
  });

  /* Media Repo */
  $('#MODAL-MEDIAREPO').each(function(e){
    var relate = $(e.relatedTarget);
    var target_input = $('input[name="'+relate.data('input')+'"]');

    var modal = $(this);
    var list_container = modal.find('#MODAL-MEDIAREPO-LIST');
    var btn_more = modal.find('#MODAL-MEDIAREPO-MORE');
    var method_container = modal.find('#MODAL-METHOD-CONTAINER');
    var uploader = modal.find('#MODAL-MEDIAREPO-UPLOADER');
    var reop_item_tmpl = modal.find('#MODAL-MEDIAREPO-ITEM');
    var mediafiles = [];

    btn_more.hide();
    reop_item_tmpl.hide();

    var attach_func = function(media_item, media){
      var media_src = media ? media.src : '';
      var media_filename = media ? media.filename : '';
      media_item.click(function(e){
        if (target_input.length) {
          target_input.val(media_src);
          target_input.change();
        }
        modal.data('media-src', media_src);
        modal.data('media-filename', media_filename);
        modal.modal('hide');
      });
    }

    var reload_media_repo = function(){
      list_container.find('.repo-item').remove();
      mediafiles.length = 0;
      load_media_files();
    }

    var load_media_files = function(){
      var offset = mediafiles.length
      $.get(modal.data('request-url'), {offset: offset}, function( data ) {
        mediafiles = mediafiles.concat(data);
        for (var i=0; i < data.length; i++){
          var media = data[i];
          var item = reop_item_tmpl.clone();
          var src = encodeURI(media.src);
          item.attr('id', null);
          item.addClass('repo-item');
          item.data('media-src', src);
          if(media.type == 'image') {
            item.find('button').css('background-image', 'url('+src+')');
            item.find('button .ico').hide();
          }
          item.find('.text').html(media.filename);
          item.show();
          attach_func(item, media);
          list_container.append(item);
        }
        if (data[0] && data[0]._more){
          btn_more.show();
        } else {
          btn_more.hide();
        }
      });
    }

    // more
    btn_more.click(function(){
      load_media_files();
    });

    // upload
    uploader.find('input[name="file"]').on('change', function(e){
      var target = e.currentTarget || e.target;
      if (target && target.value) {
        var fd = new FormData();
        var file = this.files[0];
        fd.append('file', file);
        $.ajax({
          url: uploader.attr('action'),
          type: 'post',
          data: fd,
          contentType: false,
          processData: false,
          success: function(media){
            console.info('Uploaded:', media);
            if(media.src){
              var item = reop_item_tmpl.clone();
              var src = encodeURI(media.src);
              item.attr('id', null);
              item.addClass('repo-item');
              item.data('media-src', src);
              if(media.type == 'image') {
                item.find('button').css('background-image', 'url('+src+')');
                item.find('button .ico').hide();
              }
              item.find('.text').html(media.filename);
              item.show();
              attach_func(item, media);
              reload_media_repo();
            } else {
              alert(uploader.data('error-message'))
            }
          },
        });
      }
    });

    $(this).on('show.bs.modal', function(e){
      mediafiles.length = 0;
      load_media_files()
    });
    $(this).on('hidden.bs.modal', function (e) {
      list_container.find('.repo-item').remove();
    })
  });

});