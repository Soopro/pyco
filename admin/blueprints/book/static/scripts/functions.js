(function ($) {
  $(document).ready(function() {

    $('.modal-form').each(function (e) {
      var modal = $(this);
      var form = $(modal.find('form'));
      var submit_btn = modal.find('button[type="submit"]');
      submit_btn.click(function(e){
        console.log('fuck');
        e.preventDefault();
        form.submit();
      });
    });

    $(".upload-img").each(function(e){
      var upload_form = $(this);
      $(this).find("input[type='file']").change(function(e) {
        if (!this.files || !this.files.length) {
          return
        } else if (this.files.length > 12) {
          alert('Too many files to upload. (limited to 12)');
          return
        }
        upload_form.submit();
      });
    });

    $(".qr-code").each(function(e){
      var el = $(this);
      var qr = qrcode(5, 'M');
      var text = el.attr('qr-text');
      qr.addData(text, 'Byte');
      qr.make();
      el.html(qr.createImgTag(2));
    });

    $(".print-area").click(function(e){
      var el = $('#PRINT-AREA');
      console.log(el);
      if (el) {
        var prtContent = el.html();
        var WinPrint = window.open('', '', 'left=0,top=0,width=900,height=900,toolbar=0,scrollbars=0,status=0');
        WinPrint.document.write(prtContent);
        WinPrint.document.close();
        WinPrint.focus();
        WinPrint.print();
        WinPrint.close();
      }
    });

  });
})(jQuery);