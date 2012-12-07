function close_dialog(url) {
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
                    data: { invoicing_id: $(this).data('id'),  service_name: $(this).data('service-name') }
                });
                $(this).dialog({title: "Clôture",
                    width: '500px',
                    buttons: [ { text: "Annuler",
                        click: function() { $(this).dialog("close"); } },
                    { text: "Valider",
                        click: function() { $("#change-record form").submit(); } }]});
            });
}
(function($) {
  $(function() {
    $('#hide-dossiers-cb').change(function() {
      var val = $(this).is(':checked');
      if ($(this).is(':checked')) {
        $('#dossiers-concernes div.dossier:not(.facturable)').hide('fold');
      } else {
        $('#dossiers-concernes div.dossier').show('fold');
      }
    });
    $('#close-invoicing').click(function() {
        close_dialog('clore');
    });
    $('#validate-dialog').dialog({
        autoOpen: false,
        modal: true,
        buttons: {
          "Valider": function () { $('#validate-dialog form').submit(); },
          "Annuler": function () { $(this).dialog("close"); },
        },
    });
    $('#validate').click(function () {
        $('#validate-dialog-content').load('validate/',
              function () {
                $('#validate-dialog').dialog('open');
              }
            );
      });
    $('button.blind').next().hide();
    $('button.blind').click(function() {
            $(this).next().toggle('blind');
    });
  });
})(window.jQuery)
