var path = location.pathname.split('/');
var service = path[1];
var app_name = path[2];
var current_date = path[3];
COOKIE_PATH = '/' + service + '/agenda';

function get_initial_fields(button, base) {
    var participants = new Array();
    var ressource = null;
    if ($.cookie('active-agenda')) {
        var active_agenda = $.cookie('active-agenda').split('-');
        if (active_agenda[0] == 'ressource') {
            ressource = active_agenda[1];
        } else {
            ressource = $.cookie('last-ressource');
        }
    }

    if ($.cookie('agenda-tabs')) {
        participants = $.cookie('agenda-tabs').filter(function(v) {
            var data = v.split('-');
            if(data[0]=='worker')
                return true;
        });
        participants = participants.map(function(v) {
            var data = v.split('-'); return data[1]
        });
    }
    return $.param({participants: $.makeArray(participants),
                    ressource: ressource,
                    time: $(button).data('hour'),
                    duration: $(button).data('duration')}, true);
}

function enable_new_appointment(base) {
    var base = base || 'body';
    $(base).find('.newrdv').click(function() {
        add_dialog('#ajax-dlg', $(this).data('url') + "?" + get_initial_fields(this, base), 'Nouveau rendez-vous', '880px', 'Ajouter');
    });
}

function enable_new_event(base) {
    var base = base || 'body';
    $(base).find('.newevent').click(function() {
        add_dialog('#ajax-dlg', $(this).data('url') + "?" + get_initial_fields(this, base), 'Nouvel événement', '850px', 'Ajouter');
    });
}

function enable_events(base) {
      $(base).find('.textedit').on('keydown', function() {
          $('button', this).removeAttr("disabled");
      });
      $(base).find('.textedit button').on('click', function() {
          var textarea = $(this).prev();
          var span = textarea.prev();
          var btn = $(this);
          var comment = {description: textarea.val()};
          var data = JSON.stringify(comment);
            $.ajax({
              url: '/api/v1/event/' + $(this).data("event-id") + '/?format=json&date=' + $(this).data('date'),
              type: 'PATCH',
              contentType: 'application/json',
              data: data,
              success: function(response) {
                btn.attr('disabled', 'disabled');
                if (comment['description'])
                    $('h3#' + btn.data("event-id") + ' span.icon-comment').fadeIn();
                else
                    $('h3#' + btn.data("event-id") + ' span.icon-comment').fadeOut();
                span.html('Commentaire modifié avec succès');
              }
            });
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

    enable_new_appointment(base);
    enable_new_event(base);

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
      $(base).find('.edit-event').click(function() {
          event_dialog("/" + service + "/agenda/" + current_date + "/update-event/" + $(this).data('event-id') , 'Modifier un événement', '850px', 'Modifier');
          return false;
      });

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
               if ($(this).data('address-recipient')){address += $(this).data('address-recipient') + '\n';}
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
}

function toggle_ressource(ressource) {

    var ressource_id = $(ressource).attr('id');

    var ressource_target = $(ressource).data('target');
     if (!ressource_target) {
        return;
    }

    $(ressource).toggleClass('active');
    if (!($.cookie('agenda-tabs'))) {
        $.cookie('agenda-tabs', new Array(), { path: COOKIE_PATH });
    }
    if ($(ressource).hasClass('active')) {
        var tabs = $.cookie('agenda-tabs');
        if ($.inArray(ressource_id, tabs) == -1)
        {
            tabs.push(ressource_id);
            $.cookie('agenda-tabs', tabs, { path: COOKIE_PATH });
        }
    }
    else {
        var agendatabs = $.cookie('agenda-tabs');
        if ($('#users li.item.ressource.active:last').attr('id'))
            $.cookie('last-ressource', $('#users li.item.ressource.active:last').attr('id').split('-')[1], { path: COOKIE_PATH });
        else
            $.cookie('last-ressource', '', {path: COOKIE_PATH});

        $.each(agendatabs, function (i, value) {
            if (value == ressource_id) {
                agendatabs.splice(i, 1);
            }
        });
        $.cookie('agenda-tabs', agendatabs, { path: COOKIE_PATH });
    }
    $(ressource_target).toggle();
    $('#close-all-agendas').toggle($('#users li.active').length != 0);
    if (! $('#users li.active').length) {
        $('#agendas #tabs div').hide();
    }

    var tab = $(ressource_target);
    var tab_list = $(tab).parent().get(0);
    $(tab).detach().appendTo(tab_list);

    var url = $("#date-selector").data('url');
    var tab_selector = '#' + ressource_id + '.active';

    if ($(tab_selector).length) {
        /* load disponibility column */
        $.ajaxSetup({async:false});
        $.get(url + 'disponibility/' + ressource_id,
            function(data) {
                if ($(tab_selector).hasClass('active')) {
                    var availability_block = $('ul#availability');
                    availability_block.append($(data));
                }
            }
        );
       $.ajaxSetup({async:true});
    } else {
        // remove hidden ressource availability
        $('ul#availability li.' + ressource_id).remove();
    }
    return $(ressource_target).find('a.tab');
}

function event_dialog(url, title, width, btn_text) {
    function add_periodic_events(base) {
      init_datepickers(base);
      $(base).on('click', '.update-periodic-event', function () {
        $('.ui-icon-closethick').click();
        // remove the form from previous hidden layer in order to prevent two
        // elements with 'id_date' id on the page
        $(this).parent().remove();

        var id = $(this).data('id');
        var delete_url = $(this).data('delete-url');
        var delete_button = {
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
            };
        generic_ajaxform_dialog('/' + service + '/' + app_name + '/' + current_date + '/update-periodic-event/' + id,
          'Modifier un évènement périodique', '#ajax-dlg', '900px', 'Modifier', null, init_datepickers, null, delete_button);
      });
      $(base).on('click', '.update-periodic-rdv', function () {
        $('.ui-icon-closethick').click();
        var id = $(this).data('id');
        var one_act_already_billed = $(this).data('one_act_already_billed');
        var delete_button = null
        if (one_act_already_billed == 'False') {
            var delete_url = $(this).data('delete-url');
            var delete_button = {
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
            };
        }
        generic_ajaxform_dialog('/' + service + '/' + app_name + '/' + current_date + '/update-periodic-rdv/' + id,
          'Modifier un rendez-vous périodique', '#ajax-dlg', '900px', 'Modifier', null, init_datepickers, null, delete_button);
      });
    }

    generic_ajaxform_dialog(url, title, '#ajax-dlg', width, btn_text, null,
          add_periodic_events);

}

(function($) {
  $(function() {
      $('#tabs').tabs({
          load: function(event, ui) {
              var tab = $(ui.tab).attr('id').split('-');
              if(tab[0] == 'ressource')
                  $.cookie('last-ressource', tab[1], { path: COOKIE_PATH });

              $('#tabs > div > div').accordion({active: false,
                                                autoHeight: false,
                                                collapsible: true});
              enable_events('#tabs');
          },
          selected: -1,
          collapsible: true,
      });

      $('button#print-button').click(function() { window.print();});

      enable_new_event();
      enable_new_appointment();

      if ($('#users .item').length) {
          $('#users .item').on('click', function() {
              var target = toggle_ressource(this);

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
              $.cookie('active-agenda', $(this).attr('id'), { path: COOKIE_PATH });
          });

          if ($.cookie('agenda-tabs')) {
              $.each($.cookie('agenda-tabs'), function (i, selector) {
                  toggle_ressource($('#' + selector));
              });

              if ($.cookie('active-agenda'))
              {
                  var target = $("#" + $.cookie('active-agenda')).data('target');
                  if (!$('#tabs ' + target).hasClass('ui-state-active')) {
                      $("#tabs " + target + ' a.tab').click();
                  }
              }
          }
      }

      $('a.close-tab').click(function() {
          var target = '#' + $(this).data('target');
          $(target).click();
          if ($.cookie('active-agenda') == $(target).attr('id')) {
              $.cookie('active-agenda', '', { path: COOKIE_PATH });
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
                  $('.item.worker:not(.in_service)').hide();
                  $('.item.worker:not(.intervenant)').hide();
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

    $.each({'persons': 'worker',
            'ressources': 'ressource'},
         function(key, value) {
             $('#close-all-agendas').click(function() {
                 $.cookie('active-agenda', '', {path: COOKIE_PATH});
                 $('#users .item.active').each(function (i, v) {
                     toggle_ressource(v, value);
                 });
             });
         });
  });
})(window.jQuery)
