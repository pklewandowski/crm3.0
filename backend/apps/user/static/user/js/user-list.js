import getBrokersForAdviser from './user-utils.js';

$(document).ready(function () {

    $('table#user-list-table-edit a.active').click(function (e) {
        e.preventDefault();

        var that = $(this);

        var user = {
            id: parseInt($(this).parents('tr').data('id')),
            active: $(this).children().hasClass('fa-check') ? 'False' : 'True'
        };

        Alert.questionWarning(
            "Czy na pewno zmienić aktywność użytkownika?",
            '',
            () => {
                $.ajax(window.user.active_url, {
                    method: 'POST',
                    data: {'user': user, 'csrfmiddlewaretoken': window.csrf_token},
                    complete: function (xhr) {
                        var resp = xhr.responseJSON;
                        if (resp.status != "OK") {
                            swal({
                                title: "Błąd!",
                                text: resp.message,
                                type: 'error',
                                confirmButtonText: "ok"
                            });
                        } else {
                            toogleActive(that);
                            swal('Pomyślnie zmieniono aktywność użytkownika!', '', 'success');

                        }
                    }
                });
            });
    });


    $('table#user-list-table-edit a.resetpassword').click(function (e) {
        e.preventDefault();

        let that = $(this);
        let id = parseInt($(this).parents('tr').data('id'));

        Alert.questionWarning(
            "Czy na pewno dokonać resetu hasła?",
            '',
            () => {

                $.ajax(window.user.resetpassword_url, {
                    method: 'POST',
                    data: {'id': id, 'csrfmiddlewaretoken': window.csrf_token},
                    complete: function (xhr) {
                        let resp = xhr.responseJSON;
                        if (resp.status != "OK") {
                            swal({
                                title: "Błąd!",
                                text: resp.message,
                                type: 'error',
                                confirmButtonText: "ok"
                            });
                        } else {
                            toogleActive(that);
                            swal('Pomyślnie zresetowano hasło użytkownika!', '', 'success');
                            window.location.reload();

                        }
                    }
                });
            });
    });


    $("#newAdviser").select2({
        allowClear: true,
        ajax: {
            method: 'post',
            url: _g.user.urls.getAdviserForSelect2,
            dataType: 'json',
            delay: 200,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page
                };
            }
        },
        theme: 'bootstrap',
        minimumInputLength: 2,
        language: "pl",
        // dropdownParent: $("#chooseAdviserModal")

    });

    function newAdviserList(data) {
        let tmpl = '<tr><td data-id="__BROKER_ID__">__BROKER_NAME__</td><td><select class="new-adviser-select2 form-control input-md"></select></td></tr>';

        let html = '<table class="table"><tbody>';
        data.forEach(function (item, idx) {
            html += tmpl.replace('__BROKER_ID__', item.id).replace('__BROKER_NAME__', item.name)
        });

        html += '</tbody></table>';

        $("#chooseAdviserModal #newAdviserContainer").html(html);
        $('.new-adviser-select2').select2({
            theme: 'bootstrap',
            allowClear: true,
            ajax: {
                method: 'post',
                url: _g.user.urls.getAdviserForSelect2,
                dataType: 'json'
            },
            minimumInputLength: 2,
            language: "pl",
            width: '100%'
        });
        $("#chooseAdviserModal").modal();
    }


    $(".user-delete-btn").click(function () {
        let tr = $(this).closest('tr');

        Alert.questionWarning(
            "Czy na pewno usunąć użytkownika?",
            '',
            () => {
                getBrokersForAdviser(_g.user.urls.getBrokersForAdviserUrl, tr.data('id'), null, newAdviserList);
                $("#newAdviser").val(null).trigger('change');
                $("#userId").val(tr.data('id'));
            });
    });

    $("#deleteAdviserBtn").click(function () {
        let id = $("#userId").val();
        Alert.questionWarning(
            "Jesteś pewien?",
            '',
            () => {
                $.ajax({
                    url: _g.user.urls.deleteUser,
                    method: 'POST',
                    data: {
                        id: id,
                        newAdviser: $("#newAdviser").val()
                    },

                }).done(function () {
                    swal('Pomyślnie usunięto użytkownika!', '', 'success');
                    $('#user_list').find(`tr[data-id=${id}]`).remove();


                }).fail(function (resp) {
                    swal({
                        title: "Błąd!",
                        text: resp.responseJSON.errmsg,
                        type: 'error',
                        confirmButtonText: "ok"
                    });
                });
            });
    });
});