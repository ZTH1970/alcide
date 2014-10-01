
function disable_button(button) {
  var $button = $(button);
  old_background_image = $button.css('background-image');
  old_background_repeat = $button.css('background-repeat');
  $button.data('old_background_image', old_background_image);
  $button.data('old_background_repeat', old_background_repeat);
  $button.attr('disabled', 'disabled');
  $button.css('background-image', 'url(/static/images/throbber.gif), ' + old_background_image);
  $button.css('background-repeat', 'no-repeat, ' + old_background_repeat);
}

function enable_button(button) {
  var $button = $(button);
  $button.css('background-image', $button.data('old_background_image'));
  $button.css('background-repeat', $button.data('old_background_repeat'));
  $button.removeAttr('disabled');
}

function generic_ajaxform_dialog(url, title, id, width, btn_submit_name, redirectToUrl, on_load_callback, height, extra_button, replace_content) {
  if (! height)
    height = 'auto';
  $(id).load(url,
      function () {
        init_datepickers(id);
        function onsuccess(response, status, xhr, form) {
          enable_button($('#submit-btn'));
          var parse = $(response);
          if ($('.errorlist', parse).length != 0) {
            $(id).html(response);
            on_load_callback($(id));
            $(id + ' form').ajaxForm({
              success: onsuccess,
            });
          } else if(replace_content) {
              $('body').html(parse);
          } else {
            if (redirectToUrl) {
              if (redirectToUrl.indexOf('#') == 0) {
                window.location.hash = redirectToUrl.substr(1);
                window.location.reload(true);
              } else {
                window.location = redirectToUrl;
              }
            } else if (redirectToUrl == false) {
              /* if redirectToUrl is set to false then look for the redirection
               * url in the actual page content.
               */
              var url = $(parse).find('#ajax-redirect').data('url');
              if (url) { window.location = url; }
            } else {
              window.location.reload(true);
            }
          }
        }
        $('form', this).ajaxForm({
          success: onsuccess,
        });
        var buttons = [{text: "Annuler",
                        id: "close-btn",
                        click: function() { $(this).dialog("close"); } },
                       {text:btn_submit_name,
                        id: "submit-btn",
                        click: function() {
                            disable_button($('#submit-btn'));
                            $(id + " form").submit();
                        }}];

        if (extra_button)
            buttons.push(extra_button);
        $(this).dialog({title: title,
          modal: true,
          width: width,
          height: height,
          buttons: buttons});
        if (on_load_callback) {
          on_load_callback($(this));
        }
      });
}

/**
 * Transform form(s) to ajax forms
 * id: jQuery id where you want to replace form by ajaxForm
*/
function calebasse_ajax_form(id) {
  var selector = id + ' form';
  function onsuccess(response, status, xhr, form) {
    if ($('.errorlist', response).length != 0) {
      $(id).parent().html(response);
      $(selector).ajaxForm({
        success: onsuccess,
      });
    }
    else {
      window.location.reload(true);
    }
  }
  $(selector).ajaxForm({
    success: onsuccess,
  });
}

function add_dialog(on, url, title, width, btn_text) {
  // function used to add patient schedules, events and acts

  function init_dialog() {
    $('.datepicker-date').datepicker({dateFormat: 'd/m/yy', showOn: 'button'});
    $('.datepicker input').datepicker({dateFormat: 'd/m/yy', showOn: 'button'});
    $('#id_description').attr('rows', '3');
    $('#id_description').attr('cols', '30');
    var deck = $('#id_participants_on_deck');
    $(deck).bind('added', function() {
      var added = $(deck).find('div:last');
      var t = added.attr('id').indexOf('_group:');
      if ( t == -1) return;

      /* remove group element and fake id */
      added.remove();
      var val = $('#id_participants').val();
      $('#id_participants').val(val.substr(0, val.substr(0, val.length-1).lastIndexOf('|')+1));

      /* add all workers */
      var query = added.attr('id').substr(t+1);
      var receive_result = $('#id_participants_text').autocomplete('option', 'select');
      $.getJSON($('#id_participants_text').autocomplete('option', 'source') + '?term=' + query,
        function(data) {
          $.each(data, function(key, val) {
            if (key==0) return; /* ignore first element as it's the group itself */
            var ui = Object();
            ui.item = val;
            receive_result(null, ui);
          });
        });

    });
  }

  $(on).load(url,
      function () {
        init_dialog();
        var old_background_image, old_background_repeat, $button;
        var in_submit = false;
        $(on).unbind('submit');
        $(on).submit(function(event) {
          /* stop form from submitting normally */
          event.preventDefault();

          var $form = $('form', this);
          $.post($form.attr('action'), $form.serialize(),
            function (data) {
              var parse = $(data);
              $button.css('background-image', old_background_image);
              $button.css('background-repeat', old_background_repeat);
              $button.removeAttr('disabled');
              if ($('.errorlist', parse).length != 0) {
                $(on).html(data);
                init_dialog();
              } else {
                $('body').html(data);
              }
              in_submit = false;
            },
            "html");
        });
        var submit = function (ev) {
          if (in_submit) {
            return;
          }
          in_submit = true;
          $button = $(ev.target).parent();
          old_background_image = $button.css('background-image');
          old_background_repeat = $button.css('background-repeat');
          $button.attr('disabled', 'disabled');
          $button.css('background-image', 'url(/static/images/throbber.gif), ' + old_background_image);
          $button.css('background-repeat', 'no-repeat, ' + old_background_repeat);
          $(on + " form").submit();
        };
        $(this).dialog({title: title,
          modal: true,
          width: width,
          buttons: [
        { text: btn_text,
          click: submit }
        ],
          close: function() {},
        });
      });
}

function select_add_dialog(opts, $form, form_action)
{
  var add_form = $form;

  function on_success(response, status, xhr, form) {
    var parsed_response= $(response);
    if ($('.errorlist', parsed_response).length != 0) {
      $(add_form).html($(parsed_response).find('#form-content'));
    } else {
      new_id = $('.new-object .col-id', parsed_response).text();
      new_label = $('.new-object .col-label', parsed_response).text();
      $(opts.add_select).append('<option value="' + new_id + '">' + new_label + '</option>');
      $(opts.add_select).val(new_id);
      $(opts.add_select).trigger('change');
      $(add_form).parent().dialog('close');
    }
  }

  $form.attr('action', form_action);
  $form.ajaxForm({success: on_success});
}

function init_magic_dialog() {

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

    if (opts.add_select) {
      select_add_dialog(opts, $form, form_action);
    }

    var buttons = [
    {
      text: 'Annuler',
      click: function () {
        $(this).dialog('close');
      }
    },
    {
      text: default_button,
      click: function () {
        $form.submit();
      }
    },
    ];
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
          next_url: $button.data('next-url') || false,
          add_select: $button.data('add-select') || false
        });
      });

      /* Form buttons with the '.enable-on-change' class are only enabled if an
       * input or a select of the form is modified. */
      $('form button.enable-on-change, form input[type="submit"]:not(".login")', base).prop('disabled', 'true');
      $('form input, form select, form textarea', base).on('change', function () {
        var form = $(this).closest('form');
        $('button.enable-on-change, form input[type="submit"]', form).enable();
      })
      $('form input, form textarea', base).on('keyup', function () {
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
        $input.datepicker({dateFormat: 'd/m/yy', showOn: 'button' });
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
        $input.datepicker({dateFormat: 'd/m/yy', showOn: 'button' });
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
}

(function ($) {
    init_magic_dialog();
})(window.jQuery)
