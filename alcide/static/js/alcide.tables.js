(function ($) {
  $(function () {
    /* Add click handler for tables of models */
    $('tr[data-pk]').click(function (event) {
      var pk = $(this).data('pk');
      if (! $(event.target).is('button')) {
        window.location.href=pk+'/';
      }
    });
  });
})(window.jQuery)
