var path = location.pathname.split('/');
var service = path[1];
var group_url = '/' + service + '/personnes/conges/groupe/';
var person_url = '/' + service + '/personnes/gestion/';

function action(url, worker, on, action, selector, original_color, highlight_color, params, on_success) {
    if(on) {
        if(worker)
            url += worker + '/holidays/' + on + '/' + action + '/';
        else
            url += on + '/' + action;
        $(selector).attr('style', 'background: ' + highlight_color);
    } else {
        if(worker)
            url += worker + '/holidays/' + action;
        else
            url += action;
    }
    $("#holiday-dlg").load(url,
        function() {
          $(this).dialog({title: params.title,
            width: params.width,
          buttons: [{text: params.button_close,
            click: function() {
              $(this).dialog('close');
              $(selector).attr('style', original_color);
            }},{text: params.button_confirm,
              click: function(){
                $.ajax({url: url,
                  type: 'post',
                data: $('#holiday-dlg form').serialize(),
                }
                ).done(on_success)
              }}]});
            $('form .datepicker input').trigger('focus');
            console.log('dialog loaded');
        })
};

function add_holiday(worker, url) {
    var url = url || person_url;
    params = {'title': 'Ajouter une absence', 'button_close': 'Fermer',
              'button_confirm': 'Ajouter', 'width': '550px'};

    on_success = function(response) {
        try {
            $.parseJSON(response);
            if(!response.err) {
                window.location = response.location;
            }
        } catch(e) {
            $('#holiday-dlg form').html(response);
        }
    };
    action(url, worker, null, 'ajouter', null, null, null, params, on_success);
};

function delete_holiday(worker, holiday, url) {
    var url = url || person_url;
    var selector = '#' + holiday + ' ul';
    var initial_color = $(selector).attr('style');
    var params = {'title': 'Supprimer une absence',
                  'button_close': 'Non', 'button_confirm': 'Oui',
                  'width': '450px'}

    on_success = function(response) {
      try {
          $.parseJSON(response);
          if(!response.err) {
              window.location = response.location;
          }
      } catch(e) {
          return false;
      }
    };
    action(url, worker, holiday, 'supprimer', selector, initial_color,
           '#f8b0b0', params, on_success);
};

function edit_holiday(worker, holiday, url) {
    var url = url || person_url;
    var selector = '#' + holiday + ' ul';
    var initial_color = $(selector).attr('style');
    params = {'title': 'Éditer une absence',
              'button_close': 'Fermer', 'button_confirm': 'Mettre à jour',
              'width': '550px'}

    on_success = function(response, status, xhr) {
        try {
            $.parseJSON(response);
            if(!response.err) {
                window.location = response.location;
            }
        } catch(e) {
            $('#holiday-dlg form').html(response);
        }
    }
    action(url, worker, holiday, 'editer', selector, initial_color,  '#af7', params, on_success);
};

function add_group_holiday() {
    add_holiday(null, group_url);
}

function edit_group_holiday(holiday) {
    edit_holiday(null, holiday, group_url);
};

function delete_group_holiday(holiday) {
    delete_holiday(null, holiday, group_url);
};
