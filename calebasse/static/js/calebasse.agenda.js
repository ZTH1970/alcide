function enable_events(base) {
      $(base).find('.textedit').on('keydown', function() {
          $('button', this).removeAttr("disabled");
      });
      $(base).find('.textedit button').on('click', function() {
          var textarea = $(this).prev();
          var span = textarea.prev()
          var btn = $(this)
          $.ajax({
              url: '/api/event/' + $(this).data("event-id") + '/?format=json',
              type: 'PATCH',
              contentType: 'application/json',
              data: '{"description": "' + textarea.val() + '"}',
              success: function(data) {
                  btn.attr('disabled', 'disabled');
                  span.html('Commentaire modifiée avec succès');
              }
          });
      });
      $(base).find('.appointment').on('click', function() {
          $('.textedit span', this).html('');
      });

      $(base).find('.remove-appointment').on('click', function() {
          var r = confirm("Etes-vous sûr de vouloir supprimer le rendez-vous " + $(this).data('rdv') + " ?");
          if (r == true)
          {
            $.ajax({
              url: '/api/occurrence/' + $(this).data('occurrence-id') + '/',
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
          var participants = $('.person-item.active').map(function (i, v) { return $(v).data('worker-id'); });
          var qs = $.param({participants: $.makeArray(participants), time: $(this).data('hour') }, true);
          var new_appointment_url = $(this).data('url') + "?" + qs;
          event_dialog(new_appointment_url, 'Nouveau rendez-vous', '850px', 'Ajouter');
      });
      $(base).find('.edit-appointment').click(function() {
          event_dialog("update-rdv/" + $(this).data('occurrence-id') , 'Modifier rendez-vous', '850px', 'Modifier');
          return false;
      });
      $(base).find('.newevent').click(function() {
          var participants = $('.person-item.active').map(function (i, v) { return $(v).data('worker-id'); });
          var qs = $.param({participants: $.makeArray(participants), time: $(this).data('hour') }, true);
          event_dialog($(this).data('url') + "?" + qs, 'Nouvel événement', '850px', 'Ajouter');
      });
      $(base).find('.edit-event').click(function() {
          event_dialog("update-event/" + $(this).data('occurrence-id') , 'Modifier un événement', '850px', 'Modifier');
          return false;
      });
      $(base).find('#print-button').click(function() { window.print(); });
}

function reorder_disponibility_columns() {
    /* make sure column are ordered like tabs */
    var table_indexes = new Array();
    $('a.tab').each(function(a, b) {
        table_indexes.push($(b).data('id'));
    });
    $('td#dispos table tr').each(function(a, b) {
        $(b).find('td').sortElements(function(a, b) {
          id_a = $(a).data('id');
          id_b = $(b).data('id');
          if (id_a == id_b) return 0;
          if (id_a == undefined) return -1;
          if (id_b == undefined) return 1;
          return table_indexes.indexOf(parseInt(id_a)) < table_indexes.indexOf(id_b) ? -1 : 1;
        });
    });
}

function toggle_worker(worker_selector) {
    var worker_id = $(worker_selector).data('worker-id');
    if (!worker_id) {
        return;
    }

    $(worker_selector).toggleClass('active');
    if (!($.cookie('agenda-tabs'))) {
        $.cookie('agenda-tabs', new Array(), { path: '/' });
    }
    if ($(worker_selector).hasClass('active')) {
        var tabs = $.cookie('agenda-tabs');
        if ($.inArray($(worker_selector).attr('id'), tabs) == -1)
        {
            tabs.push($(worker_selector).attr('id'));
            $.cookie('agenda-tabs', tabs, { path: '/' });
        }
    }
    else {
        var agendatabs = $.cookie('agenda-tabs');
        $.each(agendatabs, function (i, value) {
            if (value == $(worker_selector).attr('id')) {
                agendatabs.splice(i, 1);
            }
        });
        $.cookie('agenda-tabs', agendatabs, { path: '/' });
    }
    var target = $($(worker_selector).data('target'));
    target.toggle();

    var tab = $('#link-tab-worker-' + worker_id).parent().get(0);
    var tab_list = $(tab).parent().get(0);
    $(tab).detach().appendTo(tab_list);

    if ($('#tabs-worker-' + worker_id + ' .worker-tab-content-placeholder').length) {
        /* load worker appointments tab */
        $('#tabs-worker-' + worker_id).load('ajax-worker-tab/' + worker_id,
            function () {
	       $(this).children('div').accordion({active: false, autoHeight: false});
               enable_events(this);
            }
        );
        /* load worker disponibility column */
        $.get('ajax-worker-disponibility-column/' + worker_id,
            function(data) {
                var dispo_table_rows = $('td#dispos table tr');
                $(data).find('td').each(function(a, b) {
                        $(dispo_table_rows[a]).append(b);
                    }
                );
                reorder_disponibility_columns();
            }
        );
    } else {
        reorder_disponibility_columns();
    }
    return target.find('a.tab');
}

function event_dialog(url, title, width, btn_text) {
          $('#rdv').load(url,
              function () {
                  function onsuccess(response, status, xhr, form) {
                      var parse = $(response);
                      if ($('.errorlist', parse).length != 0) {
                          $('#rdv').html(response);
                          $('#rdv form').ajaxForm({
                              success: onsuccess,
                          });
                          $('#rdv .datepicker-date').datepicker({dateFormat: 'd/m/yy', showOn: 'button'});
                          console.log('error');
                      } else {
                          console.log('success');
                          window.location.reload(true);
                      }
                  }
                  $('#rdv .datepicker-date').datepicker({dateFormat: 'd/m/yy', showOn: 'button'});
                  $('#id_description').attr('rows', '3');
                  $('#id_description').attr('cols', '30');
                  $('form', this).ajaxForm({
                      success: onsuccess
                  });
                  $(this).dialog({title: title,
                      width: width,
                      buttons: [ { text: "Fermer",
                          click: function() { $(this).dialog("close"); } },
                      { text: btn_text,
                          click: function() { $("#rdv form").submit(); } }]});
              });
}

(function($) {
  $(function() {
      $('#tabs').tabs();

      $('.person-item').on('click', function() {
          var target = toggle_worker(this);
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
          $.cookie('active-agenda', $(this).data('id'), { path: '/' });
      });
      $('a.close-tab').click(function() {
          $('#' + $(this).data('target')).click()
      });

      if ($.cookie('agenda-tabs')) {
          $.each($.cookie('agenda-tabs'), function (i, worker_selector) {
              toggle_worker('#' + worker_selector);
          });
          if ($.cookie('active-agenda'))
          {
              var target = $('#link-tab-worker-' + $.cookie('active-agenda'));
              if (target.is(':visible')) {
                  target.click();
              }
          }
      }

      /* Gestion du filtre sur les utilisateurs */
      $('#filtre input').keyup(function() {
          var filtre = $(this).val();
          var everybody = $('#show-everybody').is(':checked');
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
                  $('.person-item:not(.in_service)').hide();
                  $('.person-item:not(.intervenant)').hide();
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
      enable_events($('body'));
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
  });
})(window.jQuery)
