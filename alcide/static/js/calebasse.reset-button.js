(function($) {
  $(function() {
    $('button#reset').click(function() {
        window.location.href = window.location.pathname;
        return false;
    });
  });
})(window.jQuery)
