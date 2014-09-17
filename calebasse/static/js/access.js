(function($){
    $(function() {
        $.each(['email', 'password1', 'password2'], function(i, element) {
            $('form input[name=' + element + ']').val('');
        })
    })
})(window.jQuery)
