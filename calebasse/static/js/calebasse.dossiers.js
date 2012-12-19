
function state_dialog(url, state_title, state_type) {
    $('#change-record').load(url,
            function () {
                function onsuccess(response, status, xhr, form) {
                    var parse = $(response);
                    if ($('.errorlist', parse).length != 0) {
                        $('#change-record').html(response);
                        $('#change-record form').ajaxForm({
                            success: onsuccess,
                        });
                        console.log('error');
                    } else {
                        console.log('success');
                        window.location.reload(true);
                    }
                }
                $('form', this).ajaxForm({
                    success: onsuccess,
                    data: { patient_id: $(this).data('id'),  state_type: state_type, service_id: $(this).data('service-id') }
                });
                $(this).dialog({title: "Changement - " + state_title,
                    width: '500px',
                    buttons: [ { text: "Annuler",
                        click: function() { $(this).dialog("close"); } },
                    { text: "Valider",
                        click: function() { $("#change-record form").submit(); } }]});
            });
}

(function($) {
  $(function() {
    var $tabs = $('#tabs').tabs();

    $('.atabs').click(function() {
        location.hash = 'tab=' + $(this).data('id');
    });

    $('#btn_all_state').click(function() {
      $('.checkbox_state').attr('checked', true);
    });
    $('#btn_none_state').click(function() {
      $('.checkbox_state').attr('checked', false);
    });
    $('.checkbox_state').click(function() {
        $("#search").click();
    });
    $('#id_general-pause').click(function() {
        $('#btn-maj').click();
    });
    $('.policyholder-radio').click(function() {
        $("#policyholder-form").submit();
    });
    $('.pr-line').click(function() {
        window.location.href = $(this).data('link');
    });
    $('button#reset').click(function() {
        window.location.href = window.location.pathname;
        return false;
    });

    $('#close-patientrecord').click(function() {
        state_dialog('update-state', 'Clore', 'CLOS');
    });
    $('#reopen-patientrecord').click(function() {
        state_dialog('update-state', 'Réaccueil', 'ACCUEIL');
    });
    $('#diagnostic-patientrecord').click(function() {
        state_dialog('update-state', 'Diagnostic', 'DIAGNOSTIC');
    });
    $('#traitement-patientrecord').click(function() {
        state_dialog('update-state', 'Traitement', 'TRAITEMENT');
    });
    $('#finaccueil-patientrecord').click(function() {
        state_dialog('update-state', "Fin d'accueil", 'FIN_ACCUEIL');
    });
    $('#bilan-patientrecord').click(function() {
        state_dialog('update-state', 'Bilan', 'BILAN');
    });
    $('#surveillance-patientrecord').click(function() {
        state_dialog('update-state', 'Surveillance', 'SURVEILLANCE');
    });
    $('#suivi-patientrecord').click(function() {
        state_dialog('update-state', 'Suivi', 'SUIVI');
    });
    $('#patientrecord-history').click(function() {
      $('#dossier-histo-dlg').dialog({title: 'Historique dossier',
        width: '500px',
        buttons: [ { text: "Fermer",
          click: function() { $(this).dialog("close"); } }]}
        );
    });

    $('#new-patientrecord').click(function() {
        generic_ajaxform_dialog('new', 'Nouveau dossier',
            '#dossier-dlg', '500px', 'Ajouter', false, function(that) {
                    $(that).find('#id_last_name').keyup(function() {
                            var val = $(this).val();
                            if (val.length < 3) {
                               $(that).find('#last_name_matches').empty();
                               return;
                            }
                            $.ajax({
                               url: "/lookups/ajax_lookup/patientrecord?term=" + val,
                               success: function(json) {
                                  var list = $(that).find('#last_name_matches');
                                  list.empty();
                                  $(eval(json)).each(function(a, b) {
                                          list.append($('<li><a href="' + b.pk + '/view" target="new">' + b.value + '</a></li>'));
                                  });
                               }
                            });
                    });
            });
    });
    $('#patientrecord-delete').click(function() {
        generic_ajaxform_dialog('delete', 'Supprimer le dossier',
            '#ajax-dlg', '500px', 'Oui', '..');
    });

    $('#new-address-btn').click(function() {
        generic_ajaxform_dialog('address/new', 'Ajouter une adresse',
            '#ajax-dlg', '600px', 'Ajouter');
    });
    $('.update-address-btn').click(function() {
        generic_ajaxform_dialog('address/' + $(this).data('id') + '/update', 'Modifier une adresse',
            '#ajax-dlg', '600px', 'Modifier');
    });
    $('.del-address').click(function() {
        generic_ajaxform_dialog('address/' + $(this).data('id') + '/del', 'Supprimer une addresse',
            '#ajax-dlg', '500px', 'Supprimer');
    });

    $('#update-paper-id-btn').click(function() {
        generic_ajaxform_dialog('update/paper_id', 'Modifier le numéro du dossier papier',
            '#ajax-dlg', '500px', 'Modifier');
    });

    $('#new-contact-btn').click(function() {
        generic_ajaxform_dialog('contact/new', 'Ajouter un contact',
            '#ajax-dlg', '800px', 'Ajouter', null, function(that) {
                    $(that).find('#social-security-id input').keyup(function() {
                            if ($(this).val().length < 13) {
                                $('p#nir-key span').removeAttr('id')
                                $('p#nir-key span').text('-');
                            } else {
                                $('p#nir-key span').attr('id', 'highlight')
                                var key = 97 - ($(this).val() % 97)
                                if (isNaN(key)) {
                                    $('p#nir-key span').text('NIR invalide');
                                } else {
                                    $('p#nir-key span').text(key);
                                }
                            }
                        });
            });
    });
    $('.update-contact-btn').click(function() {
        generic_ajaxform_dialog('contact/' + $(this).data('id') + '/update', 'Modifier un contact',
            '#ajax-dlg', '800px', 'Modifier');
    });
    $('.del-contact').click(function() {
        generic_ajaxform_dialog('contact/' + $(this).data('id') + '/del', 'Supprimer un contact',
            '#ajax-dlg', '500px', 'Supprimer');
    });
    $('#new-socialisation-duration-btn').click(function() {
        generic_ajaxform_dialog('socialisation/new', 'Ajouter une période de socialisation',
            '#ajax-dlg', '800px', 'Ajouter');
    });
    $('.update-duration-btn').click(function() {
        generic_ajaxform_dialog('socialisation/' + $(this).data('id') + '/update', 'Modifier une période de socialisation',
            '#ajax-dlg', '800px', 'Modifier');
    });
    $('.del-duration').click(function() {
        generic_ajaxform_dialog('socialisation/' + $(this).data('id') + '/del', 'Supprimer une période de socialisation',
            '#ajax-dlg', '500px', 'Supprimer');
    });
    $('#new-hctrait-btn').click(function() {
        generic_ajaxform_dialog('healthcare_treatment/new', 'Ajouter une prise en charge de traitement',
            '#ajax-dlg', '600px', 'Ajouter');
    });
    $('#new-hcdiag-btn').click(function() {
        generic_ajaxform_dialog('healthcare_diagnostic/new', 'Ajouter une prise en charge de diagnostic',
            '#ajax-dlg', '600px', 'Ajouter');
    });
    $('#new-notification-btn').click(function() {
        generic_ajaxform_dialog('healthcare_notification/new', 'Ajouter une notification',
            '#ajax-dlg', '600px', 'Ajouter');
    });
    $('.update-hctrait-btn').click(function() {
        generic_ajaxform_dialog('healthcare_treatment/' + $(this).data('id') + '/update', 'Modifier une prise en charge de traitement',
            '#ajax-dlg', '800px', 'Modifier');
    });
    $('.update-hcdiag-btn').click(function() {
        generic_ajaxform_dialog('healthcare_diagnostic/' + $(this).data('id') + '/update', 'Modifier une prise en charge de diagnostic',
            '#ajax-dlg', '800px', 'Modifier');
    });
    $('.update-notification-btn').click(function() {
        generic_ajaxform_dialog('healthcare_notification/' + $(this).data('id') + '/update', 'Modifier une notification',
            '#ajax-dlg', '800px', 'Modifier');
    });
    $('.del-hctrait').click(function() {
        generic_ajaxform_dialog('healthcare_treatment/' + $(this).data('id') + '/del', 'Supprimer une prise en charge de traitement',
            '#ajax-dlg', '500px', 'Supprimer');
    });
    $('.del-hcdiag').click(function() {
        generic_ajaxform_dialog('healthcare_diagnostic/' + $(this).data('id') + '/del', 'Supprimer une prise en charge de diagnostic',
            '#ajax-dlg', '500px', 'Supprimer');
    });
    $('.del-notification').click(function() {
        generic_ajaxform_dialog('healthcare_notification/' + $(this).data('id') + '/del', 'Supprimer une notification',
            '#ajax-dlg', '500px', 'Supprimer');
    });

      $('.place_of_life').click(function() {
          if ((this.checked) == true) {
              var value = "true";
          } else {
              var value = "false";
          }
          $.ajax({
              url: '/api/patientaddress/' + $(this).data("id") + '/?format=json',
              type: 'PATCH',
              contentType: 'application/json',
              data: '{"place_of_life": ' + value + '}',
              success: function(data) {
                  console.log('success');
              }
          });
      });

    $('button.blind').next().hide();
    $('button.blind').click(function() {
      $(this).next().toggle('blind');
    });
    var tabid = $.url($(location).attr('href')).fparam('tab');
    if (tabid) {
        $tabs.tabs('select',  parseInt(tabid));
    }
  });
})(window.jQuery)
