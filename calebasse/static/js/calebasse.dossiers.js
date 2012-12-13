
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
        $("#submit-policyholder").click();
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
            '#dossier-dlg', '500px', 'Ajouter');
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
            '#ajax-dlg', '800px', 'Ajouter');
    });
    $('.update-contact-btn').click(function() {
        generic_ajaxform_dialog('contact/' + $(this).data('id') + '/update', 'Modifier un contact',
            '#ajax-dlg', '800px', 'Modifier');
    });
    $('.del-contact').click(function() {
        generic_ajaxform_dialog('contact/' + $(this).data('id') + '/del', 'Supprimer un contact',
            '#ajax-dlg', '500px', 'Supprimer');
    });

    $('#add-prise-en-charge-btn').click(function() {
      $('#add-prise-en-charge-dlg').dialog({title: 'Prise en charge',
        width: '300px',
        buttons: [ { text: "Annuler",
          click: function() { $(this).dialog("close"); } },
        { text: "Valider",
          click: function() { $(this).dialog("close"); } }]}
        );
    });

    $('#add-prolongation-btn').click(function() {
      $('#add-prolongation-dlg').dialog({title: 'Prolongation',
        width: '300px',
        buttons: [ { text: "Annuler",
          click: function() { $(this).dialog("close"); } },
        { text: "Valider",
          click: function() { $(this).dialog("close"); } }]}
        );
    });
    $('#new-pctrait-btn').click(function() {
        generic_ajaxform_dialog('healthcare_treatment/new', 'Ajouter une prise en charge de traitement',
            '#ajax-dlg', '600px', 'Ajouter');
    });
    $('#new-pcdiag-btn').click(function() {
        generic_ajaxform_dialog('healthcare_diagnostic/new', 'Ajouter une prise en charge de diagnostic',
            '#ajax-dlg', '600px', 'Ajouter');
    });
    $('#new-notification-btn').click(function() {
        generic_ajaxform_dialog('healthcare_notification/new', 'Ajouter une nouvelle notification',
            '#ajax-dlg', '600px', 'Ajouter');
    });

      $('.place_of_life').click(function() {
          if ((this.checked) == true) {
          {
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
