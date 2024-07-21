function toogleIsEmployee(show) {
    if (show) {
        $("form .user-position").slideDown()
    } else {
        $("form .user-position").slideUp()
    }
}

function setRequired(isCompany, initial) {
    let required = null;

    if (isCompany) {
        required = USER_TYPE_COMPANY_REQUIRED_FIELDS[user.type];

        $('#id_user-company_name').closest('.form-group').show();
        $('#id_user-company_establish_date').closest('.form-group').show();
    } else {
        required = USER_TYPE_REQUIRED_FIELDS[user.type];
        $('#id_user-company_name').closest('.form-group').hide();
        $('#id_user-company_name').val(null);
        $('#id_user-company_establish_date').closest('.form-group').hide();
        $('#id_user-company_establish_date').val(null);
    }
    $('#user-form').find('label').removeClass('form-field-required');
    if (!initial) {
        $('#user-form').find('.form-group').removeClass('form-field-error');
        $('#user-form').find('.errorlist').remove();
    }

    $.each(required, function (i, e) {
        $('#id_user-' + e).closest('.form-group').find('label').addClass('form-field-required')
    });
}

// --------------------------------------------------------------
$(document).ready(function () {

    $(".btn-submit-user-form").click(function () {
        $("#loaderContainer").fadeIn();
        $("form#user-form").submit();
    });

    if (autocomplete_check) {
        $("form input").keyup(function (k) {
            if (k.keyCode !== 127 && k.keyCode !== 8 && (k.keyCode < 32 || k.keyCode >= 90)) {
                return false;
            }

            $.ajax(user.autocomplete_check_url, {
                method: 'get',
                data: $('form').serialize(),
                complete: function (xhr) {

                    let resp = xhr.responseJSON;

                    if (resp.status !== "OK") {
                        swal({
                            title: "Błąd!",
                            text: resp.message,
                            type: 'error',
                            confirmButtonText: "ok"
                        });
                        return;
                    }

                    //TODO: zrobić jako replace na template albo w zewnetrznej funkcji

                    var userList = '';
                    $.each(resp.data, function (i, d) {
                        userList += '<tr data-id="' + d.pk + '">' +
                            '<td>' + d.email + '</td>' +
                            '<td>' + d.first_name + ' ' + d.last_name + '</td>' +
                            '<td>' + d.personal_id + '</td>' +
                            '<td>' + d.nip + '</td>' +
                            '<td>' + d.krs + '</td>' +
                            '<td>' +
                            '<div class="btn-group">' +
                            '<a id="add_user_type_' + i + '" class="btn btn-default btn-sm dropdown-toggle" data-toggle="dropdown" href="#" aria-haspopup="true" aria-expanded="true">' +
                            '<i class="fa fa-caret-down"></i>' +
                            '</a>';

                        if (!(d.is_client && d.is_broker && d.is_adviser)) {

                            userList += '<ul class="dropdown-menu dropdown-menu-right" aria-labelledby="add_user_type_' + i + '">';
                            if (!d.is_client) {
                                userList += '<li><a href="/client/add/' + d.pk + '"><i class="fa fa-plus-square"></i> Dodaj jako klienta...</a></li>';
                            } else {
                                userList += '<li><a href="/user/edit/' + d.pk + '/CLIENT/' + '"><i class="far fa-edit"></i> Edytuj jako klienta</a></li>';
                            }
                            if (!d.is_broker) {
                                userList += '<li><a href="/broker/add/' + d.pk + '"><i class="fa fa-plus-square"></i> Dodaj jako pośrednika...</a></li>';
                            } else {
                                userList += '<li><a href="/user/edit/' + d.pk + '/BROKER/' + '"><i class="far fa-edit"></i> Edytuj jako pośrednika...</a></li>';
                            }
                            if (!d.is_adviser) {
                                userList += '<li><a href="/adviser/add/' + d.pk + '"><i class="fa fa-plus-square"></i> Dodaj jako doradcę...</a></li>';
                            } else {
                                userList += '<li><a href="/user/edit/' + d.pk + '/ADVISER/' + '"><i class="far fa-edit"></i> Edytuj jako doradcę...</a></li>';
                            }
                            if (!d.is_employee) {
                                userList += '<li><a href="/employee/add/' + d.pk + '"><i class="fa fa-plus-square"></i> Dodaj jako pracownika...</a></li>';
                            } else {
                                userList += '<li><a href="/user/edit/' + d.pk + '/EMPLOYEE/' + '"><i class="far fa-edit"></i> Edytuj jako pracownika...</a></li>';
                            }
                            userList += '</ul>';
                        }
                        // '<a class="btn btn-default btn-sm" href="/user/edit/' + d.pk + '/' + window.user.type + '"><i class="far fa-edit"></i></a>' +
                        userList += '</div>' +
                            '</td>' +
                            '</tr>';

                    });

                    $('#user_autocomplete_table').find('tbody').html(userList);
                }
            });
        });
    }

    $('form .is-employee').change(function () {
        toogleIsEmployee($(this).is(':checked'))
    });

    toogleIsEmployee($('form .is-employee').is(':checked'));

    $("#check_id_number_btn").click(function () {
        id_number = $('#id_number').val();

        $.ajax(window.user.id_exist_url, {
            method: 'GET',
            data: {'id_number': id_number, 'csrfmiddlewaretoken': window.csrf_token},
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
                }

                if (resp.id_type == 'NONE') {
                    swal({
                        title: "Błąd!",
                        text: 'Próba identyfikacji typu numeru zakończona niepowodzeniem',
                        type: 'error',
                        confirmButtonText: "ok"
                    });
                    return;

                } else if (resp.exists == true) {
                    swal({
                        title: "Błąd!",
                        text: 'Podany numer już istnieje w bazie jako ' + resp.id_type,
                        type: 'error',
                        confirmButtonText: "ok"
                    });
                    return;
                }

                $("#id_number_search_box").fadeOut(function () {
                    $(this).remove();
                    $("#form_container").html($("#form_template").html());
                    $("#form_template").remove();

                    if (resp.id_type == 'PESEL') {
                        $("form #id_user-personal_id").val(id_number);
                    } else if (resp.id_type == 'NIP') {
                        $("form #id_user-nip").val(id_number);
                    } else if (resp.id_type == 'KRS') {
                        $("form #id_user-krs").val(id_number);
                    }
                });
            }
        });
    });

    $.each($("input[name='user-hierarchy']:checked"), function (i, e) {
        $(this).closest('li').find('.user-position-list').show();
    });

    $('div.role-tree').find("input[name='user-hierarchy']").change(function () {
        let positionList = $(this).closest('li').find('.user-position-list');
        if ($(this).is(":checked")) {
            positionList.show(200);
        } else {
            positionList.hide(200);
        }


        var groups = '';
        $.each($('div.role-tree').find("input[name='user-hierarchy']:checked"), function (i, e) {
            groups += $(e).data('groups');
        });

        var groupsArray = groups.split(',').slice(0, -1);

        $("input[name='groups']").prop('checked', false);

        $.each(groupsArray, function (i, e) {
            $("input[name='groups'][value=" + e + "]").prop('checked', true);
        });
    });

    setRequired($('#id_user-is_company').is(":checked"), true);

    $('#id_user-is_company').change(function () {
        setRequired($(this).is(":checked"));
    });

    $("#id_user-avatar").fileinput({
        language: "pl",
        overwriteInitial: true,
        maxFileSize: 3000,
        showClose: false,
        showCaption: false,
        browseLabel: '',
        removeLabel: '',
        browseIcon: '<i class="glyphicon glyphicon-folder-open"></i>',
        removeIcon: '<i class="glyphicon glyphicon-remove"></i>',
        removeTitle: 'Cancel or reset changes',
        elErrorContainer: '#kv-avatar-errors-1',
        msgErrorClass: 'alert alert-block alert-danger',
        defaultPreviewContent: '<img style="max-height:160px;" src="' + imgSrc + '" alt="Awatar">',
        layoutTemplates: {main2: '{preview} {remove} {browse}'},
        allowedFileExtensions: ["jpg", "png", "gif"]
    });
});

