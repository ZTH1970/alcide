
function replace_anchor(url, anchor) {
    var splitted = url.split('#');
    return splitted[0] + '#' + encodeURI(anchor);
}

function extract_anchor() {
    if (window.location.href.indexOf('#') == -1) {
        return "";
    }
    var splitted = window.location.href.split('#');
    return decodeURI(splitted[1]).split(',');
}

function make_anchor() {
    return $.makeArray($('.person-item.active').map(function (v, i) { return '_' + $(i).attr('id'); })).join(',');
}

function toggle_worker(worker_selector) {
    $(worker_selector).toggleClass('active');
    // update the anchor
    var anchor = make_anchor();
    var new_uri = replace_anchor(window.location.href, anchor);
    console.log(new_uri);
    window.location.href = new_uri;
    $('a[href^="../"]').each(function (i, a) {
        $(a).attr('href', replace_anchor($(a).attr('href'), anchor));
    });

    var $target = $($(worker_selector).data('target'));
    $target.toggle();
    if ($target.is(':visible')) {
        $target.click();
    }
}

$(function() {
    $('#tabs').tabs();

    $('div.agenda > div').accordion({active: false, autoHeight: false});

    $('.person-item').on('click', function() {
        toggle_worker(this);
    });
    // select all anchors
    $.each(extract_anchor(), function (i, anchor) {
        $('#'+anchor.substr(1)).each(function (i, worker_selector) { toggle_worker(worker_selector); });
    });

    $('.textedit').on('keydown', function() {
        $('button', this).removeAttr("disabled");
    });
    $('.textedit button').on('click', function() {
        var textarea = $(this).prev();
        var span = textarea.prev()
        var btn = $(this)
        $.ajax({
            url: '/api/event/' + $(this).data("event-id") + '/?format=json',
            type: 'PATCH',
            contentType: 'application/json',
            data: '{"description": "' + textarea.val() + '"}',
            success: function(data) {
                btn.attr('disabled', 'disabled');
                span.html('Commentaire modifiée avec succès');
            }
        });
    });
    $('.appointment').on('click', function() {
        $('.textedit span', this).html('');
    });

    $('.remove-appointment').on('click', function() {
        var r = confirm("Etes-vous sûr de vouloir supprimer le rendez-vous " + $(this).data('rdv') + " ?");
        if (r == true)
    {
        $.ajax({
            url: '/api/occurrence/' + $(this).data('occurrence-id') + '/',
            type: 'DELETE',
            success: function(data) {
                window.location.reload(true);
                return false;
            }
        });
    }
    return false;
    });

    /* Gestion du filtre sur les utilisateurs */
    $('#filtre input').keyup(function() {
        var filtre = $(this).val();
        if (filtre) {
            $('#users li').each(function() {
                if ($(this).text().match(new RegExp(filtre, "i"))) {
                    $(this).show();
                } else {
                    $(this).hide();
                }
            });
        } else {
            $('#users li').show();
        }

    });
    $('#agenda-date').datepicker({
        dateFormat: "DD d MM yy",
        onClose: function(dateText, inst) {
            console.log('close');
        }
    });
    $('#agenda-date').on('change', function () {
        window.location.href=replace_anchor('../' + $(this).datepicker('getDate').toISOString().substr(0,10), make_anchor());
    });
    $('.date').datepicker({showOn: 'button'});
    $('#add-intervenant-btn').click(function() {
        var text = $(this).prev().val();
        $('#intervenants ul').append('<li><input type="checkbox" value="' + text + '" checked="checked">' + text + '</input></li>');
        $(this).prev().val('').focus();
        return false;
    });
    $('#newrdv').click(function() {
        var participants = $('.person-item.active').map(function (i, v) { return $(v).data('worker-id'); });
        var qs = $.param({participants: $.makeArray(participants) }, true);
        var new_appointment_url = $(this).data('url') + "?" + qs;
        $('#rdv').load(new_appointment_url,
            function () {
                function onsuccess(response, status, xhr, form) {
                    var parse = $(response);
                    if ($('.errorlist', parse).length != 0) {
                        $('#rdv').html(response);
                        $('#rdv form').ajaxForm({
                            success: onsuccess,
                        });
                        $('#rdv .datepicker-date').datepicker({dateFormat: 'yy-m-d', showOn: 'button'});
                        console.log('error');
                    } else {
                        console.log('success');
                        window.location.reload(true);
                    }
                }
                $('#rdv .datepicker-date').datepicker({dateFormat: 'yy-m-d', showOn: 'button'});
                $('form', this).ajaxForm({
                    success: onsuccess
                });
                $(this).dialog({title: 'Nouveau rendez-vous',
                    width: '820px',
                    buttons: [ { text: "Fermer",
                        click: function() { $(this).dialog("close"); } },
                    { text: "Ajouter",
                        click: function() { $("#rdv form").submit(); } }]});
            });
    });
    $('#newevent').click(function() {
        var participants = $('.person-item.active').map(function (i, v) { return $(v).data('worker-id'); });
        var qs = $.param({participants: $.makeArray(participants) }, true);
        var new_appointment_url = $(this).data('url') + "?" + qs;
        $('#rdv').load(new_appointment_url,
            function () {
                function onsuccess(response, status, xhr, form) {
                    var parse = $(response);
                    if ($('.errorlist', parse).length != 0) {
                        $('#rdv').html(response);
                        $('#rdv form').ajaxForm({
                            success: onsuccess,
                        });
                        $('#rdv .datepicker-date').datepicker({dateFormat: 'yy-m-d', showOn: 'button'});
                        console.log('error');
                    } else {
                        console.log('success');
                        window.location.reload(true);
                    }
                }
                $('#rdv .datepicker-date').datepicker({dateFormat: 'yy-m-d', showOn: 'button'});
                $('#id_description').attr('rows', '3');
                $('#id_description').attr('cols', '30');
                $('form', this).ajaxForm({
                    success: onsuccess
                });
                $(this).dialog({title: 'Nouvelle événement',
                    width: '850px',
                    buttons: [ { text: "Fermer",
                        click: function() { $(this).dialog("close"); } },
                    { text: "Ajouter",
                        click: function() { $("#rdv form").submit(); } }]});
            });
    });
});

