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
  });
})(window.jQuery)
