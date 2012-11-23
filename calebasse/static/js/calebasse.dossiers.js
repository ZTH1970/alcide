
(function($) {
    $(function() {
        $('#btn_all_state').click(function() {
            $('.checkbox_state').attr('checked', true);
        });
        $('#btn_none_state').click(function() {
            $('.checkbox_state').attr('checked', false);
        });
    });
})(window.jQuery)

