function add_datepickers(that) {
  $('input#id_start_date', that).datepicker({dateFormat: 'd/m/yy', showOn: 'button' });
  $('input#id_request_date', that).datepicker({dateFormat: 'd/m/yy', showOn: 'button' });
  $('input#id_agree_date', that).datepicker({dateFormat: 'd/m/yy', showOn: 'button' });
  $('input#id_insist_date', that).datepicker({dateFormat: 'd/m/yy', showOn: 'button' });
  $('input#id_end_date', that).datepicker({dateFormat: 'd/m/yy', showOn: 'button' });
  $('input#id_date_selected', that).datepicker({dateFormat: 'd/m/yy', showOn: 'button' });
  $('input#id_prolongation_date', that).datepicker({dateFormat: 'd/m/yy', showOn: 'button' });
}

function load_add_address_dialog() {
    generic_ajaxform_dialog('address/new', 'Ajouter une adresse',
        '#address-dlg', '600px', 'Ajouter');
}

function state_dialog(url, state_title, state_type) {
    $('#change-record').load(url,
            function () {
                var patient_id = $(this).data('id');
                var service_id = $(this).data('service-id');
                function onsuccess(response, status, xhr, form) {
                    var parse = $(response);
                    if ($('.errorlist', parse).length != 0) {
                        $('#change-record').html(response);
                        $('#change-record form').ajaxForm({
                            success: onsuccess,
                            data: { patient_id: patient_id,  state_type: state_type, service_id: service_id }
                        });
                    } else {
                        window.location.reload(true);
                    }
                }
                if (state_type == 'CLOS_RDV') {
                  var message = $('p.message')
                  message.append($('<span id="highlight">Attention ce patient a encore des rendez-vous de planifiés !</span>'));
                  state_type = 'CLOS';
                }
                $('input.date', this).datepicker({dateFormat: 'd/m/yy', showOn: 'button' });
                $('form', this).ajaxForm({
                    success: onsuccess,
                    data: { patient_id: patient_id,  state_type: state_type, service_id: service_id }
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
        $('#general-form').submit();
    });
    $('#id_general-confidential').click(function() {
        $('#general-form').submit();
    });
    $('.policyholder-radio').click(function() {
        $("#policyholder-form").submit();
    });
    $('.pr-line').click(function() {
        window.open($(this).data('link'), $(this).data('link'));
    });
    $('button#reset').click(function() {
        window.location.href = window.location.pathname;
        return false;
    });
    $('#print-button').click(function() { window.print(); });

    $('#close-patientrecord').click(function() {
        state_dialog('update-state', 'Clore', 'CLOS');
    });
    $('#close-rdv-patientrecord').click(function() {
        state_dialog('update-state', 'Clore', 'CLOS_RDV');
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
    if (location.hash.indexOf('histo') != -1) {
      $('#patientrecord-history').click();
      location.hash = '';
    }

    $('#new-patientrecord').click(function() {
        generic_ajaxform_dialog('new', 'Nouveau dossier',
            '#dossier-dlg', '700px', 'Ajouter', false, function(that) {
                    $('input#id_date_selected', that).datepicker({dateFormat: 'd/m/yy', showOn: 'button' });
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

    function nir_check(that) {
      $(that).find('#social-security-id input').keyup(function() {
        if ($(this).val().length < 13) {
             $('p#nir-key span').removeAttr('id')
             $('p#nir-key span').text('-');
         } else {
             $('p#nir-key span').attr('id', 'highlight')
             var nir = $(this).val();
             var minus = 0;
             if (nir.charAt(6) == 'A'){
               nir = nir.replace('A', '0');
               minus = 1000000;
             }
             if (nir.charAt(6) == 'B'){
               nir = nir.replace('B', '0');
               minus = 2000000;
             }
             nir = parseInt(nir, 10);
             nir = nir - minus;
             var key = 97 - (nir % 97);
             if (isNaN(key)) {
                 $('p#nir-key span').text('NIR invalide');
             } else {
                 $('p#nir-key span').text(key);
             }
         }
      });
    }

    $('#new-contact-btn').click(function() {
        generic_ajaxform_dialog('contact/new', 'Ajouter un contact',
            '#ajax-dlg', '900px', 'Ajouter', null, nir_check);
    });
    $('.update-contact-btn').click(function() {
        generic_ajaxform_dialog('contact/' + $(this).data('id') + '/update', 'Modifier un contact',
            '#ajax-dlg', '800px', 'Modifier', null, nir_check);
    });
    $('.del-contact').click(function() {
        generic_ajaxform_dialog('contact/' + $(this).data('id') + '/del?address=' + $(this).data('address-id'),
                'Supprimer un contact', '#ajax-dlg', '500px', 'Supprimer');
    });
    $('#new-socialisation-duration-btn').click(function() {
        generic_ajaxform_dialog('socialisation/new', 'Ajouter une période de socialisation',
            '#ajax-dlg', '800px', 'Ajouter', null, add_datepickers);
    });
    $('.update-duration-btn').click(function() {
        generic_ajaxform_dialog('socialisation/' + $(this).data('id') + '/update', 'Modifier une période de socialisation',
            '#ajax-dlg', '800px', 'Modifier', null, add_datepickers);
    });
    $('.del-duration').click(function() {
        generic_ajaxform_dialog('socialisation/' + $(this).data('id') + '/del', 'Supprimer une période de socialisation',
            '#ajax-dlg', '500px', 'Supprimer');
    });
    $('#new-protection-btn').click(function() {
        generic_ajaxform_dialog('protection/new', 'Ajouter une mesure de protection',
            '#ajax-dlg', '800px', 'Ajouter', null, add_datepickers);
    });
    $('.update-protection-btn').click(function() {
        generic_ajaxform_dialog('protection/' + $(this).data('id') + '/update', 'Modifier une mesure de protection',
            '#ajax-dlg', '800px', 'Modifier', null, add_datepickers);
    });
    $('.del-protection').click(function() {
        generic_ajaxform_dialog('protection/' + $(this).data('id') + '/del', 'Supprimer une mesure de protection',
            '#ajax-dlg', '500px', 'Supprimer');
    });
    $('#new-mdph-request-btn').click(function() {
        generic_ajaxform_dialog('mdph_request/new', 'Ajouter une demande MDPH',
            '#ajax-dlg', '800px', 'Ajouter', null, add_datepickers);
    });
    $('.update-mdph-request-btn').click(function() {
        generic_ajaxform_dialog('mdph_request/' + $(this).data('id') + '/update', 'Modifier une demande MDPH',
            '#ajax-dlg', '800px', 'Modifier', null, add_datepickers);
    });
    $('.del-mdph-request').click(function() {
        generic_ajaxform_dialog('mdph_request/' + $(this).data('id') + '/del', 'Supprimer une demande MDPH',
            '#ajax-dlg', '500px', 'Supprimer');
    });
    $('#new-mdph-response-btn').click(function() {
        generic_ajaxform_dialog('mdph_response/new', 'Ajouter une réponse MDPH',
            '#ajax-dlg', '800px', 'Ajouter', null, add_datepickers);
    });
    $('.update-mdph-response-btn').click(function() {
        generic_ajaxform_dialog('mdph_response/' + $(this).data('id') + '/update', 'Modifier une réponse MDPH',
            '#ajax-dlg', '800px', 'Modifier', null, add_datepickers);
    });
    $('.del-mdph-response').click(function() {
        generic_ajaxform_dialog('mdph_response/' + $(this).data('id') + '/del', 'Supprimer une réponse MDPH',
            '#ajax-dlg', '500px', 'Supprimer');
    });
    $('#new-hctrait-btn').click(function() {
        generic_ajaxform_dialog('healthcare_treatment/new', 'Ajouter une prise en charge de traitement',
            '#ajax-dlg', '600px', 'Ajouter', null, add_datepickers);
    });
    $('#new-hcdiag-btn').click(function() {
        generic_ajaxform_dialog('healthcare_diagnostic/new', 'Ajouter une prise en charge de diagnostic',
            '#ajax-dlg', '600px', 'Ajouter', null, add_datepickers);
    });
    $('#new-notification-btn').click(function() {
        generic_ajaxform_dialog('healthcare_notification/new', 'Ajouter une notification',
            '#ajax-dlg', '600px', 'Ajouter', null, add_datepickers);
    });
    $('.update-hctrait-btn').click(function() {
        generic_ajaxform_dialog('healthcare_treatment/' + $(this).data('id') + '/update', 'Modifier une prise en charge de traitement',
            '#ajax-dlg', '800px', 'Modifier', null, add_datepickers);
    });
    $('.update-hcdiag-btn').click(function() {
        generic_ajaxform_dialog('healthcare_diagnostic/' + $(this).data('id') + '/update', 'Modifier une prise en charge de diagnostic',
            '#ajax-dlg', '800px', 'Modifier', null, add_datepickers);
    });
    $('.update-notification-btn').click(function() {
        generic_ajaxform_dialog('healthcare_notification/' + $(this).data('id') + '/update', 'Modifier une notification',
            '#ajax-dlg', '800px', 'Modifier', null, add_datepickers);
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

    $('.update-patient-state-btn').click(function() {
        generic_ajaxform_dialog('state/' + $(this).data('id') + '/update', 'Modifier un état',
            '#ajax-dlg', '500px', 'Modifier', '#histo', add_datepickers);
    });
    $('.del-patient-state-btn').click(function() {
        generic_ajaxform_dialog('state/' + $(this).data('id') + '/del', 'Supprimer un état',
            '#ajax-dlg', '500px', 'Supprimer', '#histo');
    });


      $('.place_of_life').click(function() {
          if ((this.checked) == true) {
              var value = "true";
          } else {
              var value = "false";
          }
          var prev = $(this).prev();
          $.ajax({
              url: '/api/v1/patientaddress/' + $(this).data("id") + '/?format=json',
              type: 'PATCH',
              contentType: 'application/json',
              data: '{"place_of_life": ' + value + '}',
              success: function(data) {
                (prev).show();
                (prev).html('<li>Modification appliquée avec succés</li>');
                $('.ajax_messages').delay(1500).fadeOut('slow');
              }
          });
      });

    $('input#id_id-birthdate', this).datepicker({dateFormat: 'd/m/yy', showOn: 'button' });

    $('button.blind').next().hide();
    $('button.blind').click(function() {
      $(this).next().toggle('blind');
    });
    $('#social-security-label').click(function() {
      var label = $(this).html();
      var data = $(this).next();
      if (($(data).is(':hidden'))) {
        $(this).html(label.replace('+', '-'));
        $(this).css("font-weight", "bold");
      } else {
        $(this).html(label.replace('-', '+'));
        $(this).css("font-weight", "");
      }
      $(data).toggle();
    });
    $('#prescription-transport-btn').click(function() {
        $('#ajax-dlg').load('prescription-transport',
          function () {
             $(this).dialog({title: 'Prescription de transport', width: '800px',
                      buttons: [ { text: "Fermer",
                          click: function() { $(this).dialog("close"); } },
                      { text: "Prescrire",
                          click: function() { $("#ajax-dlg form").submit(); $(this).dialog("close"); } }]});
             $('.addresses input[type=radio]').first().click();
         });
         return false;
    });
    var tabid = $.url($(location).attr('href')).fparam('tab');
      if (tabid) {
        $tabs.tabs('select',  parseInt(tabid));
      }
    });

})(window.jQuery)

$( document ).ready(function(){
    var hashes = location.hash.split('&');
    for (i in hashes) {
      console.log(hashes[i]);
      if (hashes[i] == "newcontact") {
        $('#new-contact-btn').first().click();
      }
    }
    location.hash = hashes[0];
});
