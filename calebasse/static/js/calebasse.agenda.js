var path = location.pathname.split('/');
var service = path[1];
var app_name = path[2];
var current_date = path[3];
COOKIE_PATH = '/' + service + '/agenda';

function delete_prompt(text) {
  var r = prompt(text + '\n Pour cela veuillez entrer DEL');
  if (r.toLowerCase().replace(/^\s+|\s+$/g, '') == 'del') {
    return true;
  } else {
    return false;
  }
}
function enable_events(base) {
      $(base).find('.textedit').on('keydown', function() {
          $('button', this).removeAttr("disabled");
      });
      $(base).find('.textedit button').on('click', function() {
          var textarea = $(this).prev();
          var span = textarea.prev()
          var btn = $(this)
          if ($(this).data('act-id'))
          {
            var data = {comment: textarea.val() };
            var data = JSON.stringify(data);
            $.ajax({
              url: '/api/v1/act/' + $(this).data("act-id") + '/?format=json&date=' + $(this).data('date'),
              type: 'PATCH',
              contentType: 'application/json',
              data: data,
              success: function(data) {
                btn.attr('disabled', 'disabled');
                span.html('Commentaire modifié avec succès');
              }
            });
          }
          else
          {
            var data = {description: textarea.val() };
            var data = JSON.stringify(data);
            $.ajax({
              url: '/api/v1/event/' + $(this).data("event-id") + '/?format=json&date=' + $(this).data('date'),
              type: 'PATCH',
              contentType: 'application/json',
              data: data,
              success: function(data) {
                btn.attr('disabled', 'disabled');
                span.html('Commentaire modifié avec succès');
              }
            });
          }
      });
      /* TODO: put this in a generic function */
      $('.input_is_billable').click(function() {
          if ($(this).data("switch-billable") == "True") {
              var value = "false";
          } else {
              var value = "true";
          }
          $.ajax({
              url: '/api/v1/act/' + $(this).data("id") + '/?format=json',
              type: 'PATCH',
              contentType: 'application/json',
              data: '{"switch_billable": ' + value + '}',
              success: function(data) {
              }
          });
      });
      $('.input_is_lost').click(function() {
          if ((this.checked) == true) {
              var value = "true";
          } else {
              var value = "false";
          }
          $.ajax({
              url: '/api/v1/act/' + $(this).data("id") + '/?format=json',
              type: 'PATCH',
              contentType: 'application/json',
              data: '{"is_lost": ' + value + '}',
              success: function(data) {
              }
          });
      });

      $(base).find('.appointment').on('click', function() {
          $('.textedit span', this).html('');
      });

      $(base).find('.remove-appointment').on('click', function() {
          var r = delete_prompt("Etes-vous sûr de vouloir supprimer le rendez-vous " + $(this).data('rdv') + " ?");
          if (r == true)
          {
            $.ajax({
              url: $(this).data('url'),
              type: 'DELETE',
              success: function(data) {
                  window.location.reload(true);
                  return false;
              }
            });
           }
        return false;
      });
      $(base).find('.newrdv').click(function() {
          var participants = new Array();
          if ($.cookie('agenda-worker-tabs')) {
              participants = $.cookie('agenda-worker-tabs').map(function(i, v) { var data = i.split('-'); return data[2]});
          }
          var qs = $.param({participants: $.makeArray(participants),
                            room: $.cookie('active-ressource-agenda'),
                            time: $(this).data('hour') }, true);
          var new_appointment_url = $(this).data('url') + "?" + qs;
          event_dialog(new_appointment_url, 'Nouveau rendez-vous', '850px', 'Ajouter');
      });
      $(base).find('.edit-appointment').click(function() {
        id = $(this).data("event-id");
        $.getJSON("/api/v1/eventwithact/" + id + "/?format=json")
          .done(function () {
            event_dialog("/" + service + "/agenda/" + current_date + "/update-rdv/" + id,
              'Modifier rendez-vous', '850px', 'Modifier');
          })
         .fail(function() {
            window.location.reload(true);
            $('.messages').html("Le rendez-vous n'existe plus");
            return false;
         });
        return false;
      });
      $(base).find('.newevent').click(function() {
          var participants = new Array();
          if ($.cookie('agenda-worker-tabs')) {
              var participants = $.cookie('agenda-worker-tabs').map(function(i, v) { var data = i.split('-'); return data[2]});
          }
          var qs = $.param({participants: $.makeArray(participants),
                            room: $.cookie('active-ressource-agenda'),
                            time: $(this).data('hour') }, true);
          event_dialog($(this).data('url') + "?" + qs, 'Nouvel événement', '850px', 'Ajouter');
      });
      $(base).find('.edit-event').click(function() {
          event_dialog("/" + service + "/agenda/" + current_date + "/update-event/" + $(this).data('event-id') , 'Modifier un événement', '850px', 'Modifier');
          return false;
      });
      $(base).find('#print-button').click(function() { window.print(); });

      $('.generate-mail-btn', base).click(function() {
        var url = '../../dossiers/' + $(this).data('dossier-id') + '/generate?event-id=' + $(this).data('event-id') + '&date=' + $(this).data('date');
        $('#ajax-dlg').load(url,
          function () {
            $(this).dialog({title: 'Générer un courrier', width: '500px',
                      buttons: [ { text: "Fermer",
                          click: function() { $(this).dialog("close"); } },
                      { text: "Générer",
                          click: function() { $("#ajax-dlg form").submit(); $(this).dialog("close"); } }]});
             $(this).find('.addresses input[type=radio]').change(function() {
               var address = '';
               if ($(this).data('contact-gender')){address += $(this).data('contact-gender') + ' ';}
               if ($(this).data('contact-first-name')){address += $(this).data('contact-first-name') + ' ';}
               if ($(this).data('contact-last-name')){address += $(this).data('contact-last-name') + '\n';}
               if ($(this).data('address-number')){address += $(this).data('address-number') + ' ';}
               if ($(this).data('address-street')){address += $(this).data('address-street') + '\n';}
               if ($(this).data('address-address-complement')){address += $(this).data('address-address-complement') + '\n';}
               if ($(this).data('address-zip-code')){address += $(this).data('address-zip-code') + ' ';}
               if ($(this).data('address-city')){address += $(this).data('address-city') + '\n';}
               $('#id_address').val(address);
               $('#id_phone_address').val($(this).attr('data-address-phone'));
             });
             $('.addresses input[type=radio]').first().click();
          });
        return false;
      });
      $(base).on('click', '.update-periodic-event', function () {
        $('.ui-icon-closethick').click();
        // remove the form from previous hidden layer in order to prevent two
        // elements with 'id_date' id on the page
        $(this).parent().remove();

        var id = $(this).data('id');
        var delete_url = $(this).data('delete-url');
        generic_ajaxform_dialog('/' + service + '/' + app_name + '/' + current_date + '/update-periodic-event/' + id,
          'Modifier un évènement périodique', '#ajax-dlg', '900px', 'Modifier', null,
          function (dialog) {
            $('#ajax-dlg .datepicker-date').datepicker({dateFormat: 'd/m/yy', showOn: 'button'});
            var buttons = $(dialog).dialog('option', 'buttons');
            buttons.push({
              text: "Supprimer",
              id: "delete-btn",
              click: function () {
                var r = delete_prompt("Etes-vous sûr de vouloir supprimer cet évènement récurrent ?");
                if (r == true)
                {
                  $.ajax({
                    url: delete_url,
                    type: 'DELETE',
                    success: function(data) {
                        window.location.reload(true);
                        return false;
                    }
                  });
                }
              }
            });
            $(dialog).dialog('option', 'buttons', buttons);
          }
        );
      });
      $(base).on('click', '.update-periodic-rdv', function () {
        $('.ui-icon-closethick').click();
        var id = $(this).data('id');
        var delete_url = $(this).data('delete-url');
        generic_ajaxform_dialog('/' + service + '/' + app_name + '/' + current_date + '/update-periodic-rdv/' + id,
          'Modifier un rendez-vous périodique', '#ajax-dlg', '900px', 'Modifier', null,
          function (dialog) {
            $('#ajax-dlg .datepicker-date').datepicker({dateFormat: 'd/m/yy', showOn: 'button'});
            var buttons = $(dialog).dialog('option', 'buttons');
            buttons.push({
              text: "Supprimer",
             id: "delete-btn",
              click: function () {
                var r = delete_prompt("Etes-vous sûr de vouloir supprimer ce rendez-vous récurrent ?");
                if (r == true)
                {
                  $.ajax({
                    url: delete_url,
                    type: 'DELETE',
                    success: function(data) {
                        window.location.reload(true);
                        return false;
                    }
                  });
                }
              }
            });
            $(dialog).dialog('option', 'buttons', buttons);
          }
        );
      });
}

function reorder_disponibility_columns() {
    /* make sure column are ordered like tabs */
    var table_indexes = new Array();
    $('a.tab').each(function(a, b) {
        table_indexes.push($(b).data('id'));
    });

    rows = $('td#dispos table tr');
    for (var i=0; i<rows.length; i++) {
        tr = $(rows[i]);
        t = $.map(table_indexes,
                  function(v, i) { return $('.ressource-' + v, tr)[0]; }).filter(
                  function(a) { if (a) return true; return false; });
        $('.agenda', tr).detach();
        $(tr).append(t);
    };
}

function toggle_ressource(ressource_selector, ressource) {

    var ressource_id = $(ressource_selector).data(ressource + '-id');
     if (!ressource_id) {
        return;
    }

    $(ressource_selector).toggleClass('active');
    if (!($.cookie('agenda-' + ressource + '-tabs'))) {
        $.cookie('agenda-' + ressource + '-tabs', new Array(), { path: COOKIE_PATH });
    }
    if ($(ressource_selector).hasClass('active')) {
        var tabs = $.cookie('agenda-' + ressource + '-tabs');
        if ($.inArray($(ressource_selector).attr('id'), tabs) == -1)
        {
            tabs.push($(ressource_selector).attr('id'));
            $.cookie('agenda-' + ressource + '-tabs', tabs, { path: COOKIE_PATH });
        }
    }
    else {
        var agendatabs = $.cookie('agenda-' + ressource + '-tabs');
        $.each(agendatabs, function (i, value) {
            if (value == $(ressource_selector).attr('id')) {
                agendatabs.splice(i, 1);
            }
        });
        $.cookie('agenda-' + ressource + '-tabs', agendatabs, { path: COOKIE_PATH });
    }
    var target = $($(ressource_selector).data('target'));
    target.toggle();
    $('#close-all-' + ressource + '-agendas').toggle($('li.agenda:visible').length != 0);

    var tab = $('#link-tab-' + ressource + '-' + ressource_id).parent().get(0);
    var tab_list = $(tab).parent().get(0);
    $(tab).detach().appendTo(tab_list);

    var url = $("#date-selector").data('url');

    var tab_selector = '';
    if (ressource == 'worker') {
        tab_selector = '#selector-' + ressource + '-' + ressource_id + '.active';
    } else {
        tab_selector = '#selector-ressource-' + ressource_id + '.active';
    }

    if ($(tab_selector).length) {
        /* load disponibility column */
        $.get(url + 'ajax-' + ressource + '-disponibility-column/' + ressource_id,
            function(data) {
                if ($(tab_selector).hasClass('active')) {
                    var dispo_table_rows = $('td#dispos table tr');
                    all_td = $(data).find('td');
                    $(data).find('td').each(function(a, b) {
                        $(dispo_table_rows[a]).append(b);
                    });
                }
            }
        );
    } else {
        // remove hidden ressource availability
        $('td#dispos table tr td.ressource-' + ressource_id + '.agenda').remove();
    }

    reorder_disponibility_columns();
    return target.find('a.tab');
}

function event_dialog(url, title, width, btn_text) {
    add_dialog('#ajax-dlg', url, title, width, btn_text);
}

(function($) {
  $(function() {
      $('#tabs').tabs({
          load: function(event, ui) {
              $('#tabs > div > div').accordion({active: false,
                                                autoHeight: false,
                                                collapsible: true});
              enable_events($('body'));
          },
          selected: -1,
          collapsible: true,
      });

      $('#tabs').ajaxStop(function() { reorder_disponibility_columns(); });

      if ($('.worker-item').length) {
          $('.worker-item').on('click', function() {
              var target = toggle_ressource(this, 'worker');

              if ($(target).is(':visible')) {
                  $(target).click();
              }
              if ($('#filtre input').val()) {
                  $('#filtre input').val('');
                  $('#filtre input').keyup();
                  $('#filtre input').focus();
              }
             if (! ($('li.agenda:visible').hasClass('ui-state-active'))) {
                $('li.agenda:visible:last a.tab').click();
              }
          });

          $('a.tab').click(function() {
              $.cookie('active-worker-agenda', $(this).data('id'),  { path: COOKIE_PATH });
          });

          if ($.cookie('agenda-worker-tabs')) {
              $.each($.cookie('agenda-worker-tabs'), function (i, worker_selector) {
                  toggle_ressource('#' + worker_selector, 'worker');
              });
              if ($.cookie('active-worker-agenda'))
              {
                  var target = $('#link-tab-worker-' + $.cookie('active-worker-agenda'));
                  if (target.is(':visible')) {
                      target.click();
                  }
              }
          }
      }

      if ($('.ressource-item').length) {
          $('.ressource-item').on('click', function() {
              var target = toggle_ressource(this, 'ressource');
              if ($(target).is(':visible')) {
                  $(target).click();
              }
              if ($('#filtre input').val()) {
                  $('#filtre input').val('');
                  $('#filtre input').keyup();
                  $('#filtre input').focus();
              }
          });

          $('a.tab').click(function() {
              $.cookie('active-ressource-agenda', $(this).data('id'), { path: COOKIE_PATH });
          });

          if ($.cookie('agenda-ressource-tabs')) {
              $.each($.cookie('agenda-ressource-tabs'), function (i, ressource_selector) {
                  toggle_ressource('#' + ressource_selector, 'ressource');
              });
              if ($.cookie('active-ressource-agenda'))
              {
                  var target = $('#link-tab-ressource-' + $.cookie('active-ressource-agenda'));
                  if (target.is(':visible')) {
                      target.click();
                  }
              }
          }
      }

      $('a.close-tab').click(function() {
          var target = '#' + $(this).data('target');
          $(target).click();
          if ($.cookie('active-ressource-agenda') == $(target).data('ressource-id')) {
              $.cookie('active-ressource-agenda','', { path: COOKIE_PATH });
          }

      });


      /* Gestion du filtre sur les utilisateurs */
      $('#filtre input').keyup(function() {
          var filtre = $(this).val();
          if ($('#show-everybody').length) {
              var everybody = $('#show-everybody').is(':checked');
          } else {
              var everybody = true;
          }
          if (filtre) {
              $('#show-everybody').attr('checked', true);
              $('#users li').each(function() {
                  if ($(this).text().match(new RegExp(filtre, "i"))) {
                      $(this).show();
                  } else {
                      $(this).hide();
                  }
              });
          } else {
              $('#users li').show();
              if (! everybody) {
                  $('.worker-item:not(.in_service)').hide();
                  $('.worker-item:not(.intervenant)').hide();
              }
          }
          /* hide worker type titles that do not have a single visible person */
          $("#users ul:has(*):has(:visible)").parent().prev().show();
          $("#users ul:has(*):not(:has(:visible))").parent().prev().hide();
      });

      $('.date').datepicker({showOn: 'button'});
      $('#add-intervenant-btn').click(function() {
          var text = $(this).prev().val();
          $('#intervenants ul').append('<li><input type="checkbox" value="' + text + '" checked="checked">' + text + '</input></li>');
          $(this).prev().val('').focus();
          return false;
      });
      $('#show-everybody').change(function() {
      if (! $(this).is(':checked')) {
        $('#filtre input').val('');
      }
      $('#filtre input').keyup();
      return;
    });
    $('select[name^="act_state"]').on('change', function () {
    $(this).next('button').prop('disabled',
      ($(this).data('previous') == $(this).val()));
    })
    $('#filtre input').keyup();

    $.each({'persons': {'button': 'worker', 'element': 'worker'},
            'rooms': {'button': 'ressource', 'element': 'ressource'}
           },
         function(key, value) {
             $('#close-all-' + value.button + '-agendas').click(function() {
                 $.cookie('active-' + value.element + '-agenda', '', {path: COOKIE_PATH});
                 $('.' + value.element + '-item.active').each(function (i, v) {
                     toggle_ressource(v, value.element);
                 });
             });
         });
  });
})(window.jQuery)
