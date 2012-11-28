
function state_dialog(url, state_name) {
    $('#change-record').load(url,
            function () {
                function onsuccess(response, status, xhr, form) {
                    var parse = $(response);
                    if ($('.errorlist', parse).length != 0) {
                        $('#change-record').html(response);
                        $('#change-record form').ajaxForm({
                            success: onsuccess,
                        });
                        // $('#change-record .datepicker-date').datepicker({dateFormat: 'd/m/yy', showOn: 'button'});
                        console.log('error');
                    } else {
                        console.log('success');
                        window.location.reload(true);
                    }
                }
                $('#change-record .datepicker-date').datepicker({dateFormat: 'd/m/yy', showOn: 'button'});
                $('form', this).ajaxForm({
                    success: onsuccess,
                    data: { patient_id: $(this).data('id'),  new_state_name: state_name }
                });
                $(this).dialog({title: "Changement - " + state_name,
                    width: '500px',
                    buttons: [ { text: "Annuler",
                        click: function() { $(this).dialog("close"); } },
                    { text: "Valider",
                        click: function() { $("#change-record form").submit(); } }]});
            });
}

(function($) {
  $(function() {
    $('#btn_all_state').click(function() {
      $('.checkbox_state').attr('checked', true);
    });
    $('#btn_none_state').click(function() {
      $('.checkbox_state').attr('checked', false);
    });
    $('.pr-line').click(function() {
        window.location.href = $(this).data('link');
    });

    $('#close-patientrecord').click(function() {
        state_dialog('update-state', 'Clore');
    });
    $('#tabs').tabs();
    $('#reaccueillir-dossier').click(function() {
      $('#dossier-change').dialog({title: 'Changement - Réaccueil',
        width: '500px',
        buttons: [ { text: "Annuler",
          click: function() { $(this).dialog("close"); } },
        { text: "Valider",
          click: function() { $(this).dialog("close"); } }]}
        );
    });
    $('#historique-dossier').click(function() {
      $('#dossier-histo-dlg').dialog({title: 'Historique dossier',
        width: '500px',
        buttons: [ { text: "Fermer",
          click: function() { $(this).dialog("close"); } }]}
        );
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
  });
})(window.jQuery)

