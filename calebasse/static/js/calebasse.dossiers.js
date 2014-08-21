function add_datepickers(that) {
  $('input#id_birthdate', that).datepicker({dateFormat: 'd/m/yy', showOn: 'button',
    changeMonth: true, changeYear: true, yearRange: 'c-80:c+2' });
  $('input#id_start_date', that).datepicker({dateFormat: 'd/m/yy', showOn: 'button' });
  $('input#id_request_date', that).datepicker({dateFormat: 'd/m/yy', showOn: 'button' });
  $('input#id_agree_date', that).datepicker({dateFormat: 'd/m/yy', showOn: 'button' });
  $('input#id_insist_date', that).datepicker({dateFormat: 'd/m/yy', showOn: 'button' });
  $('input#id_end_date', that).datepicker({dateFormat: 'd/m/yy', showOn: 'button' });
  $('input#id_date_selected', that).datepicker({dateFormat: 'd/m/yy', showOn: 'button' });
  $('input#id_prolongation_date', that).datepicker({dateFormat: 'd/m/yy', showOn: 'button' });
}

function print_cleanup() {
    $.each($('textarea'), function() {
        if(!$(this).val())
            $(this).addClass('screen-only');
        else
            $(this).removeClass('screen-only');
    });
}

function filter_date_bounds(tab, container, selector) {
    var from = $(tab + ' form.filter input[name=from]').datepicker('getDate');
    var to = $(tab + ' form.filter input[name=to]').datepicker('getDate');
    if (to) {
        to.setHours(23); to.setMinutes(59); to.setSeconds(59);
    }
    $.each($(tab + ' ' + container), function(element) {
        var block = $(this);
        block.addClass('screen-only');
        if ($(selector, $(this)).length) {
            $.each($(selector, this), function() {
                var current = $.datepicker.parseDate('d/m/yy', $(this).text());
                if (current < from || (to && current >= to)) {
                    $(this).parent().parent().addClass('screen-only');
                } else {
                    block.removeClass('screen-only');
                    $(this).parent().parent().removeClass('screen-only');
                }
            });
        }
    })
};

function load_add_address_dialog() {
  var str = $("#contactform").serialize();
  $.cookie('contactform', str, { path: window.location.pathname });
  generic_ajaxform_dialog('address/new', 'Ajouter une adresse',
      '#address-dlg', '600px', 'Ajouter');
}

function warning_on_unsave_change() {
    var form_changed = false;
    $(window).on("beforeunload", function() {
        if (form_changed) {
            return "Vous n'avez pas enregistré vos changements.";
        }
    });
    $("#tabs").on("tabsbeforeactivate", function(event, ui) {
        if (form_changed) {
            var answer = confirm('Vous avez des changements non sauvegardés. Voulez vous vraiment continuer ?');
            if (! answer) {
                event.preventDefault();
            }
            else {
                form_changed = false;
            }
        }
    });
    $('.autosubmit').on("click", function() {
        form_changed = false;
    });
    $('form').on("change", function() {
        form_changed = true;
    });
    $('button').on("click", function() {
        form_changed = false;
    });
    var tabid = parseInt($.url($(location).attr('href')).fparam('tab')) + 1;
    if ($('.errorlist', '#ui-tabs-' + tabid).length != 0) {
      form_changed = true;
    }
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

function load_tab1_general() {
    warning_on_unsave_change();
    $('#update-paper-id-btn').click(function() {
        generic_ajaxform_dialog('update/paper_id', 'Modifier le numéro du dossier papier',
            '#ajax-dlg', '500px', 'Modifier');
    });
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
    $('.autosubmit').click(function() {
        $('#general-form').submit();
    });
}

function load_tab2_adm() {
}

function load_tab3_addresses() {
    function nir_check(that) {
      add_datepickers($(that));
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
    $('.policyholder-radio').click(function() {
        $("#policyholder-form").submit();
    });
    $('#new-contact-btn').click(function() {
        generic_ajaxform_dialog('contact/new', 'Ajouter un contact',
            '#ajax-dlg', '900px', 'Ajouter', null, nir_check, 850);
    });
    $('.update-contact-btn').click(function() {
        generic_ajaxform_dialog('contact/' + $(this).data('id') + '/update', 'Modifier un contact',
            '#ajax-dlg', '800px', 'Modifier', null, nir_check, null, null, true);
    });
    $('.del-contact').click(function() {
        generic_ajaxform_dialog('contact/' + $(this).data('id') + '/del?address=' + $(this).data('address-id'),
                'Supprimer un contact', '#ajax-dlg', '500px', 'Supprimer');
    });
    $('#new-address-btn').click(function() {
        generic_ajaxform_dialog('address/new', 'Ajouter une adresse',
            '#ajax-dlg', '600px', 'Ajouter');
    });
    $('.update-address-btn').click(function() {
        generic_ajaxform_dialog('address/' + $(this).data('id') + '/update', 'Modifier une adresse',
            '#ajax-dlg', '600px', 'Modifier', null, null, null, null, true);
    });
    $('.del-address').click(function() {
        generic_ajaxform_dialog('address/' + $(this).data('id') + '/del', 'Supprimer une addresse',
            '#ajax-dlg', '500px', 'Supprimer');
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
              async: false,
              contentType: 'application/json',
              data: '{"place_of_life": ' + value + '}',
              success: function(data) {
                (prev).show();
                (prev).html('<li>Modification appliquée avec succés</li>');
                $('.ajax_messages').delay(1500).fadeOut('slow');
                location.reload();
              }
          });
      });
    var hashes = location.hash.split('&');
    for (i in hashes) {
      if (hashes[i] == "newcontact") {
        var form = $.cookie('contactform');
        generic_ajaxform_dialog('contact/new?'+ form, 'Ajouter un contact',
            '#ajax-dlg', '900px', 'Ajouter', null, nir_check, 850);
        $.removeCookie('contactform', { path: window.location.pathname });
      }
    }
    location.hash = hashes[0];
}

function load_tab4_notifs() {
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

}

function load_tab5_last_acts() {
}

function load_tab6_next_rdv() {
}

function load_tab7_socialisation() {
    $('#new-socialisation-duration-btn').on("click", function() {
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
}

function load_tab8_medical() {
  calebasse_ajax_form('#tabs-8');
  warning_on_unsave_change();
}


(function($) {
  $(function() {
    var $tabs = $('#tabs').tabs({
      load: function(event, ui) {
        $('.js-click-to-expand').on('click', function (event) {
             $(event.target).parents('.js-expandable').toggleClass('js-expanded');
             $(event.target).next().toggle();
        });
        var tabid = $(ui.tab).attr('id');
        if (tabid == "ui-id-1")
            load_tab1_general();
        else if (tabid == "ui-id-2")
            load_tab2_adm();
        else if (tabid == "ui-id-3")
            load_tab3_addresses();
        else if (tabid == "ui-id-4")
            load_tab4_notifs();
        else if (tabid == "ui-id-7")
            load_tab7_socialisation();
        else if (tabid == "ui-id-8")
            load_tab8_medical();
      },
        selected: -1,
        collapsible: true,
    });


    $('#tabs').on("tabsload", function(event, ui) {
        location.hash = 'tab=' + $(ui.tab).data('id');
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

    $('.pr-line').click(function() {
        window.open($(this).data('link'), $(this).data('link'));
    });
    $('button#reset').click(function() {
        window.location.href = window.location.pathname;
        return false;
    });
    $('#print-button').click(function() {
        var button = $(this);
        var title = button.html();
        button.html('Préparation de l\'impression en cours');
        button.attr({disabled: 'disabled'});
        button.toggleClass('icon-wip');
        $('.pagination').next().remove();
        $.get(window.location + '&all', function(data) {
            button.toggleClass('icon-wip');
            button.removeAttr('disabled');
            button.html(title);
            $('.content').append(data);
            window.print();
        });
    });

    $('#patientrecord-print-button').on('click', function(event) {
        event.preventDefault();
        generic_ajaxform_dialog($(this).attr('href'), 'Impression dossier patient',
                                '#ajax-dlg', '450px', 'Imprimer', false, false);
    });

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


    $('.update-patient-state-btn').click(function() {
        generic_ajaxform_dialog('state/' + $(this).data('id') + '/update', 'Modifier un état',
            '#ajax-dlg', '500px', 'Modifier', '#histo', add_datepickers);
    });
    $('.del-patient-state-btn').click(function() {
        generic_ajaxform_dialog('state/' + $(this).data('id') + '/del', 'Supprimer un état',
            '#ajax-dlg', '500px', 'Supprimer', '#histo');
    });

    $('button.blind').next().hide();
    $('button.blind').click(function() {
      $(this).next().toggle('blind');
    });
    var tabid = $.url($(location).attr('href')).fparam('tab');
      if (tabid) {
        $tabs.tabs('select',  parseInt(tabid));
      }
      else {
        $tabs.tabs('select',  0);
      }
    });

})(window.jQuery)

