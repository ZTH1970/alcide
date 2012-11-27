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
    $('#tabs').tabs();
    $('#clore-dossier').click(function() {
      $('#dossier-change').dialog({title: 'Changement - Clôture',
        width: '500px',
        buttons: [ { text: "Annuler",
          click: function() { $(this).dialog("close"); } },
        { text: "Valider",
          click: function() { $(this).dialog("close"); } }]}
        );
    });
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

