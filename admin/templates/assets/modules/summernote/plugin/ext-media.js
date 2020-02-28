(function(factory) {
  /* global define */
  if (typeof define === 'function' && define.amd) {
    // AMD. Register as an anonymous module.
    define(['jquery'], factory);
  } else if (typeof module === 'object' && module.exports) {
    // Node/CommonJS
    module.exports = factory(require('jquery'));
  } else {
    // Browser globals
    factory(window.jQuery);
  }
}(function($) {
  // Extends plugins for adding hello.
  //  - plugin is external module for customizing.
  $.extend($.summernote.plugins, {
    /**
     * @param {Object} context - context object has status of editor.
     */
    'media': function(context) {
      var self = this;

      // ui has renders to build ui elements.
      //  - you can create a button with `ui.button`
      var ui = $.summernote.ui;
      var lang = context.options.langInfo;

      // add button
      context.memo('button.media', function() {
        // create button
        var button = ui.button({
          contents: '<i class="note-icon-picture"/>',
          tooltip: lang.image.image,
          click: function() {
            if (self.$panel) {
              self.$panel.data('for-summernote', true);
              self.$panel.modal('show');
            }
          },
        });

        // create jQuery object from button instance.
        var $media_btn = button.render();
        return $media_btn;
      });

      // This events will be attached when editor is initialized.
      this.events = {
        // This will be called after modules are initialized.
        'summernote.init': function(we, e) {
          // console.log('summernote initialized', we, e);
        },
        // This will be called when user releases a key on editable.
        'summernote.keyup': function(we, e) {
          // console.log('summernote keyup', we, e);
        },
      };

      var media_modal_handler = function (e) {
        if (self.$panel && self.$panel.data('for-summernote')) {
          var img_src = self.$panel.data('media-src');
          var filename = self.$panel.data('media-filename');
          self.$panel.data('for-summernote', false);
          if (img_src) {
            img_el = '<img src="'+img_src+'" alt="'+filename+'"/>'
            context.invoke('editor.pasteHTML', img_el);
            // context.invoke('editor.insertImage', img_src, filename);
            // `insertImage` will load the image and set image width.
            // which is I don't want to.
          }
        }
      }

      this.initialize = function() {
        this.$panel = $(context.$note.attr('media-modal')).modal('hide');
        if(this.$panel.length == 0){
          this.$panel = null;
          console.error('Summernote Plugin: Media modal not found!')
        } else {
          self.$panel.on('hide.bs.modal', media_modal_handler);
        }
      };

      // This methods will be called when editor is destroyed by $('..').summernote('destroy');
      // You should remove elements on `initialize`.
      this.destroy = function() {
        if (self.$panel){
          self.$panel.off('hide.bs.modal', media_modal_handler);
        }
      };
    },
  });
}));
