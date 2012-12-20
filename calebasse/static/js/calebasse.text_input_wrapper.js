(function ($) {
  $(function() {
      $('.text-input-wrapper .clear').click(function () {
        $(this).prev('input').val('');
        $(this).closest('form').submit();
      });
      $("input:text:visible:first").focus();
  });
})(window.jQuery)
