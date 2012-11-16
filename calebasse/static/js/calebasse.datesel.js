(function($) {
  $(function () {
    $('#date-selector').datepicker({
        dateFormat: "DD d MM yy",
        onClose: function(dateText, inst) {
            console.log('close');
        }
    });
    $('#date-selector').on('change', function () {
        var date = $(this).datepicker('getDate')
        var year = date.getFullYear();
        var month = date.getMonth() + 1;
        var day = date.getDate();
        var url_tpl = $(this).data('url');
        var new_date = year + '-' + month + '-' + day;
        var url = url_tpl.replace(/[0-9]{4}-[0-9]{2}-[0-9]{2}/, new_date);
        window.location.href = url;
    });
  });
})(window.jQuery)
