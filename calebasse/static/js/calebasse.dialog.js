(function ($) {
  $.fn.dialogButton = function (opts) {
    var id = $(this).attr('id');
    this.on('click', function () {
      var $dialog = $('<div id="dialog-' + (opts.name || id) + 
                     '" title="' + opts.title + '"><form class="inline-form" method="post"></form></div>');
      var default_button = opts.default_button == undefined ? 'Envoyer' : opts.default_button;
      var form_action = opts.url.split(' ')[0];
      var $form = $('form', $dialog);
      $dialog.appendTo('#dialogs');
      $form.attr('action', form_action);
      var buttons = [{
          text: default_button,
          click: function () {
            $form.submit();
          }
        },
        {
          text: 'Annuler',
          click: function () {
              $(this).dialog('close');
          }
        }];
      $dialog.css('max-height', $(window).height() - 200);
      $form.load(opts.url, function () {
        $dialog.dialog({
          modal: opts.modal == undefined ? true : opts.modal,
          width: 700,
          maxHeight: $(window).height() - 100,
          buttons: buttons,
          close: function () {
            $(this).remove();
          }
        });
      });
    })
  };
  $(function () {
    $('.dialog-button').each(function (i, button) {
      var $button = $(button);
      $button.dialogButton({
        url: $button.data('url') || $button.closest('a').attr('href'),
        default_button: $button.data('default-button') || $button.text(),
        title: $button.attr('title') || $button.text(),
      });
    });

    /* Form buttons with the '.enable-on-change' class are only enabled if an
     * input or a select of the form is modified. */
    $('form button.enable-on-change, form input[type="submit"]').prop('disabled', 'true');
    $('form input, form select').on('change', function () {
      var form = $(this).closest('form');
      $('button.enable-on-change, form input[type="submit"]', form).enable();
    })
    $('form input').on('keyup', function () {
      var form = $(this).closest('form');
      $('button.enable-on-change, form input[type="submit"]', form).enable();
    })
  });
})(window.jQuery)
