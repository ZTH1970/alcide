(function($) {
  $(function () {
    try {
        // in case of the #date-selector element doesn't exist
        var value = $('#date-selector').attr('value');
        var week = value.substring(value.indexOf('(') + 1, value.length - 1);
        var format = "DD d MM yy (" + week + ")";
    } catch(err) {
        var format = "DD d MM yy";
    };
    $('#date-selector').datepicker({
        dateFormat: format,
        showWeek: true,
        onClose: function(dateText, inst) {
        }
    });
    $('#date-selector').on('change', function () {
        var date = $(this).datepicker('getDate');
        var year = date.getFullYear();
        var month = date.getMonth() + 1;
        var first_jan = new Date(year, 0, 1);
        var dayOfYear = ((date - first_jan + 1) / 86400000);
        var week = Math.ceil(dayOfYear/7);
        var day = date.getDate();
        var current_date = $(this).attr('value');
        current_date = current_date.replace(/\([0-9]{2}\)/, '(' + week + ')');
        $(this).attr('value', current_date);
        var url_tpl = $(this).data('url');
        var new_date = year + '-' + month + '-' + day;
        var url = url_tpl.replace(/[0-9]{4}-[0-9]{2}-[0-9]{2}/, new_date);
        window.location.href = url;
    });
  });
})(window.jQuery)
