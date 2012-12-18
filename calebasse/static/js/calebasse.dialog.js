
function generic_ajaxform_dialog(url, title, id, width, btn_submit_name, redirectToUrl, on_load_callback) {
  $(id).load(url,
      function () {
        function onsuccess(response, status, xhr, form) {
          var parse = $(response);
          if ($('.errorlist', parse).length != 0) {
            $(id).html(response);
            $(id + ' form').ajaxForm({
              success: onsuccess,
            });
            console.log('error');
          } else {
            console.log('success');
            if (redirectToUrl) {
              window.location = redirectToUrl;
            }
            else {
              window.location.reload(true);
            }
          }
        }
        $('form', this).ajaxForm({
          success: onsuccess,
        });
        $(this).dialog({title: title,
          width: width,
          buttons: [ { text: "Annuler",
            click: function() { $(this).dialog("close"); } },
          { text: btn_submit_name,
            click: function() { $(id + " form").submit(); } }]});
	if (on_load_callback) {
            on_load_callback($(this));
	}
      });
}

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
      if (opts.next_url) {
          $form.attr('action', form_action + '?next_url=' + opts.next_url);
      } else {
          $form.attr('action', form_action);
      }
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
          width: 900,
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
    window.calebasse_dialogs = function(base) {

      var base = base || $('body').get(0);
      $('.dialog-button', base).each(function (i, button) {
        var $button = $(button);
        $button.dialogButton({
          url: $button.data('url') || $button.closest('a').attr('href'),
          default_button: $button.data('default-button') || $button.text(),
          title: $button.attr('title') || $button.text(),
          next_url: $button.data('next-url') || false
        });
      });

      /* Form buttons with the '.enable-on-change' class are only enabled if an
       * input or a select of the form is modified. */
      $('form button.enable-on-change, form input[type="submit"]', base).prop('disabled', 'true');
      $('form input, form select', base).on('change', function () {
        var form = $(this).closest('form');
        $('button.enable-on-change, form input[type="submit"]', form).enable();
      })
      $('form input', base).on('keyup', function () {
        var form = $(this).closest('form');
        $('button.enable-on-change, form input[type="submit"]', form).enable();
      })
      $('form.form-with-confirmation', base).on('submit', function () {
          var mesg = $(this).data('confirmation-msg') || "Êtes-vous sûr ?";
          return window.confirm(mesg);
      });
      $('form .datepicker', base).each(function (i, span) {
        var $span = $(span);
        var $input = $('input', span);
        var months = $span.data('number-of-months');
        var before_selector = $span.data('before-selector');
        var after_selector = $span.data('after-selector');
        $input.datepicker({dateFormat: 'd/m/yy' });
        if (months) {
          $input.datepicker("option", "numberOfMonths", months);
        }
        if (before_selector) {
          var $before_target = $('input', $(before_selector));
          $input.datepicker("option", "maxDate", $before_target.val());
          $input.datepicker("option", "onClose", function (selectedDate) {
            $before_target.datepicker( "option", "minDate", selectedDate );
          });
        }
        if (after_selector) {
          var $after_target = $('input', $(after_selector));
          $input.datepicker("option", "minDate", $after_target.val());
          $input.datepicker("option", "onClose", function (selectedDate) {
            $after_target.datepicker( "option", "maxDate", selectedDate );
          });
        }
      });
      $('form .reset', base).on('click', function () {
        var $this = $(this);
        var $form = $($this.closest('form'));
        $('input', $form).val('');
      });
      $('body').on('focus', 'form .datepicker input', function (e) {
        var $input = $(e.target);
        var $span = $($input.closest('.datepicker'));
        var months = $span.data('number-of-months');
        var before_selector = $span.data('before-selector');
        var after_selector = $span.data('after-selector');
        if ($input.is('.hasDatepicker')) {
          return true;
        }
        $input.datepicker({dateFormat: 'd/m/yy' });
        if (months) {
          $input.datepicker("option", "numberOfMonths", months);
        }
        if (before_selector) {
          var $before_target = $('input', $(before_selector));
          $input.datepicker("option", "maxDate", $before_target.val());
          $input.datepicker("option", "onClose", function (selectedDate) {
            $before_target.datepicker( "option", "minDate", selectedDate );
          });
        }
        if (after_selector) {
          var $after_target = $('input', $(after_selector));
          $input.datepicker("option", "minDate", $after_target.val());
          $input.datepicker("option", "onClose", function (selectedDate) {
            $after_target.datepicker( "option", "maxDate", selectedDate );
          });
        }
      });
    };
    window.calebasse_dialogs();
  });
})(window.jQuery)
