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

  /* form */
  $('form').each(function(){
    var form = $(this);
    form.find('.reset-form').on('click', function(){
      form.trigger("reset");
    });
  });

  $('.multientry-form').each(function(){
    var form = $(this);
    var field_tmpl = form.find('.TMPL');
    var fields_container = form.find('.fields');
    var btn_add_field = form.find('.add-field');
    var TEMPLATE = '';
    if (field_tmpl.length) {
      TEMPLATE = field_tmpl.html();
      field_tmpl.remove();
    } else {
      console.warn('multientry: TEMPLATE IS MISSING.')
    }
    function attach_handler(entry){
      entry.find('.remove-field').on('click', function(e){
        entry.remove();
      });
      entry.find('.move-field-up').on('click', function(e){
        entry.insertBefore(entry.prev('.field-entry'));
      });
      entry.find('.move-field-down').on('click', function(e){
        entry.insertAfter(entry.next('.field-entry'));
      });
    }
    form.find('.fields .field-entry').each(function(){
      attach_handler($(this));
    });
    btn_add_field.on('click', function(){
      var new_entry = $(TEMPLATE);
      attach_handler(new_entry);
      fields_container.append(new_entry);
    });

  });


  /* Uploader */

  $('.file-uploader').each(function(){
    var uploader = $(this);
    uploader.find('input[name="file"]').on('change', function(e){
      if ($(this).val()) {
        uploader.submit();
      }
    });
    uploader.find('input[name="files"][multiple]').on('change', function(e){
      if ($(this).val()) {
        var limit = parseInt($(this).attr('maxlength')) || 60;
        if (this.files.length <= limit) {
          uploader.submit();
        } else {
          alert($(this).attr('maxlength-error'));
        }
      }
    });
  });

  /* prevent ENTER key */
  $('.prevent-enter-key').on('keyup keypress', function(e) {
    var keyCode = e.keyCode || e.which;
    if (keyCode === 13) {
      e.preventDefault();
      return false;
    }
  });

  /* Media Input Field */
  $('.media-preview-field').each(function(){
    var media_input = $(this).find('.media-input');
    var preview = $(this).find('.media-preview');
    var preview_lnk = preview.find('a');
    var allowed_exts = ['jpg', 'jpe', 'jpeg', 'png', 'gif', 'svg'];

    function _is_img(url){
      if (!url || typeof(url) != 'string'){
        return false;
      } else {
        var ends = url.split('.').pop();
        return allowed_exts.indexOf(ends) >= 0;
      }
    }
    function _toggle_preview() {
      var url = media_input.val();
      if(_is_img(url)){
        preview_lnk.attr('href', url).css('background-image','url('+url+')');
        preview.show();
      } else {
        preview_lnk.attr('href', '#').css('background-image','none');
        preview.hide();
      }
    }
    _toggle_preview();
    media_input.on('change', function(e){
      _toggle_preview();
    });
  });

  /* Media Repo */
  $('#MODAL-MEDIAREPO').each(function(index, element){
    var relate, target_input;
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
        if (target_input && target_input.length) {
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
      if ($(this).val()) {
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

    modal.on('show.bs.modal', function(e){
      modal.data('media-src', '');
      modal.data('media-filename', '');
      mediafiles.length = 0;
      relate = $(e.relatedTarget);
      target_input = relate.parent().parent().find(
        'input[name="'+relate.data('input')+'"]');
      load_media_files()
    });
    modal.on('hidden.bs.modal', function (e) {
      list_container.find('.repo-item').remove();
    })
  });

});