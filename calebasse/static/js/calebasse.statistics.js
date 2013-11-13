(function($) {
  $(function() {
    $('.stats').click(function() {
        var url = 'form/' + this.id;
        $('#ajax-dlg').load(url,
          function () {
             $(this).dialog({title: 'Choix des parametres', width: '700px',
                      buttons: [ { text: "Fermer",
                          click: function() { $(this).dialog("close"); } },
                      { text: "Extraire",
                          click: function() { $("#ajax-dlg form").submit(); $(this).dialog("close"); } }]});
              var deck = $('#id_participants_on_deck');
              $(deck).bind('added', function() {
                  var added = $(deck).find('div:last');
                  var t = added.attr('id').indexOf('_group:');
                  if ( t == -1) return;
                  var query = added.attr('id').substr(t+1);

                  /* remove group element and fake id */
                  added.remove();
                  var val = $('#id_participants').val();
                  $('#id_participants').val(val.substr(0, val.substr(0, val.length-1).lastIndexOf('|')+1));

                  /* add all workers */
                  var receive_result = $('#id_participants_text').autocomplete('option', 'select');
                  $.getJSON($('#id_participants_text').autocomplete('option', 'source') + '?term=' + query,
                      function(data) {
                          $.each(data, function(key, val) {
                              if (key==0) return; /* ignore first element as it's the group itself */
                              var ui = Object();
                              ui.item = val;
                              receive_result(null, ui);
                          });
                  });
              });
         });
         return false;
    });
  });
})(window.jQuery)
