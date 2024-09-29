$(document).ready(function () {

    $('.entry-edit-btn').click(function () {

        var that = $(this);

        //$('#entry-edit-dlg .modal-body').data({'status-name': that.data('status-name'), 'status-value': that.data('status-value'), 'id': that.data('id')});

        $('#entry-edit-dlg').data({'mode': 'E', 'id': that.parents('tr').data('id-entry')});
        $('#entry-edit-dlg .modal-title').text('Edycja wpisu');

        $('#entry-edit-dlg #id_entry-label').val(that.parents('tr').children('td.entry-label').text());
        $('#entry-edit-dlg #id_entry-value').val(that.parents('tr').children('td.entry-value').text()); //.data('entry-value'))
        $('#entry-edit-dlg #id_entry-value').prop('readonly', true);

        openModalDialog($('#entry-edit-dlg'));
    });

    $('.entry-add-btn').click(function () {

        var that = $(this);

        //$('#entry-edit-dlg .modal-body').data({'status-name': that.data('status-name'), 'status-value': that.data('status-value'), 'id': that.data('id')});

        $('#entry-edit-dlg').data({'mode': 'C'});
        $('#entry-edit-dlg .modal-title').text('Nowy wpis');

        $('#entry-edit-dlg #id_entry-value').val(null);
        $('#entry-edit-dlg #id_entry-label').val(null);

        if (window.dict.type == 'LV')  // TODO: docelowo nie drutować, wziąć ze zmiennej konfiguracyjnej
        {
            $('#entry-edit-dlg #id_entry-value').prop('readonly', false);
        } else {
            $('#entry-edit-dlg #id_entry-value').prop('readonly', true);
        }

        openModalDialog($('#entry-edit-dlg'));
    });

    $('#entry-edit-dlg .modal-footer .save').click(function () {

        var url;
        var entry = {'value': $('#entry-edit-dlg #id_entry-value').val(), 'label': $('#entry-edit-dlg #id_entry-label').val(), 'id_dict': window.dict.id};

        if ($('#entry-edit-dlg').data('mode') == 'E') {
            entry['id'] = $('#entry-edit-dlg').data('id');
            url = window.dict.entry_edit_url;
        }
        else {
            url = window.dict.entry_add_url;
        }

        $.ajax(url, {
            method: 'POST',
            data: {'entry': entry, 'csrfmiddlewaretoken': window.csrf_token},
            complete: function (xhr) {
                var resp = xhr.responseJSON;
                if (resp.status != "OK") {
                    swal({
                        title: "Błąd!",
                        text: resp.message,
                        type: 'error',
                        confirmButtonText: "ok"
                    });
                    return;
                } else {
                    swal({'title': 'Pomyślnie zapisano wpis słownika!', 'type': 'success'},
                        function () {
                            window.location.reload();
                        });

                }
            }
        });
    });

    $('#entry_list a.active').click(function (e) {
        e.preventDefault();

        var that = $(this);

        var entry = {
            id: parseInt($(this).parents('tr').data('id-entry')),
            active: $(this).children().hasClass('fa-check') ? 'False' : 'True'
        };


        $.ajax(window.dict.entry_active_url, {
            method: 'POST',
            data: {'entry': entry, 'csrfmiddlewaretoken': window.csrf_token,},
            complete: function (xhr) {
                var resp = xhr.responseJSON;
                if (resp.status != "OK") {
                    swal({
                        title: "Błąd!",
                        text: resp.message,
                        type: 'error',
                        confirmButtonText: "ok"
                    });
                    return;
                } else {
                    toogleActive(that);
                    swal('Pomyślnie zmieniono stan wpisu!', '', 'success');

                }
            }
        });
    });
});
