
function generic_form_dialog(url, title, id, width, btn_submit_name, redirectToUrl) {
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
            });
}

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
        generic_form_dialog('new', 'Nouveau dossier',
            '#dossier-dlg', '500px', 'Ajouter');
    });
    $('#patientrecord-delete').click(function() {
        generic_form_dialog('delete', 'Supprimer le dossier',
            '#delete-record', '500px', 'Oui', '..');
    });

    $('#new-address-btn').click(function() {
      $('#new-address-dlg').dialog({title: 'Nouvelle adresse',
        width: '500px',
        buttons: [ { text: "Annuler",
          click: function() { $(this).dialog("close"); } },
        { text: "Valider",
          click: function() { $(this).dialog("close"); } }]}
        );
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

    $('button.blind').next().hide();
    $('button.blind').click(function() {
      $(this).next().toggle('blind');
    });
    var tabid = $.url($(location).attr('href')).fparam('tab');
    if (tabid) {
        $tabs.tabs('select',  parseInt(tabid));
        location.hash = '';
    }
  });
})(window.jQuery)

