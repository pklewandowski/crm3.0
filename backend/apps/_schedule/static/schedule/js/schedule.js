/**
 * Ajax schedule event database operations
 */

function create_post() {
    $.ajax({
        url: "/schedule/schedule-add/",
        type: "POST",
        data: $("form#schedule-form").serialize(),
        success: function () {
            resetCalendarMode();
            $('#calendar').fullCalendar('refetchEvents');
            $('#addScheduleFormModal').modal('toggle');

            var title = !$('form#schedule-form #id').val() ? 'Pomyślnie dodano zdarzenie!' : 'Pomyślnie zaktualizowano zdarzenie!';
            swal({
                title: title,
                text: '.',
                type: 'info',
                confirmButtonText: "ok"
            });
        },
        error: function (response) {

            var resp = response.responseJSON;

            swal({
                title: "Błąd!",
                text: resp.errmsg,
                type: 'error',
                confirmButtonText: "ok"
            });

            if (typeof resp.form_errors !== "undefined") {
                if (typeof resp.form_errors.ScheduleForm !== "undefined") {

                    $.each(resp.form_errors.ScheduleForm, function (i, e) {

                        var formGroup = $('#id_schedule-' + i).closest('div.form-group');
                        formGroup.addClass('form-field-error');

                        var errors = '';
                        $.each(e, function (i, e) {
                            errors += '<li>' + e + '</li>';
                        });

                        formGroup.append('<ul class="errorlist">' + errors + '<ul>');

                        var error_list = $('#addScheduleFormModal').find('#error_list');
                        error_list.text('Wystąpiły błędy!');
                        error_list.show(200);

                    });
                }
            }
        }
    });
}

function getEventData(event, url) {

    $.ajax(url, {
        dataType: 'json',
        method: 'POST',
        data: {'id': event.id, 'csrfmiddlewaretoken': csrf_token},
        success: function (res) {
            if (res.status !== "OK") {
                swal({
                    title: "Błąd!",
                    text: res.errMSG,
                    type: 'error',
                    confirmButtonText: "ok"
                });
                return false;
            } else {

                let event_data = [];

                if (res.schedule) {
                    event_data['schedule'] = $.parseJSON(res.schedule)[0];
                } else {
                    event_data['schedule'] = null;
                }

                if (res.messages) {
                    event_data['messages'] = $.parseJSON(res.messages);
                } else {
                    event_data['messages'] = null;
                }

                if (res.event_type) {
                    event_data['event_type'] = $.parseJSON(res.event_type)[0];
                } else {
                    event_data['event_type'] = null;
                }

                if (res.users) {
                    event_data['users'] = $.parseJSON(res.users);
                } else {
                    event_data['users'] = null;
                }

                if (res.custom_address) {
                    event_data['custom_address'] = $.parseJSON(res.custom_address)[0];
                } else {
                    event_data['custom_address'] = null;
                }

                if (res.meeting_room) {
                    event_data['meeting_room'] = $.parseJSON(res.meeting_room)[0];
                } else {
                    event_data['meeting_room'] = null;
                }

                if (res.created_by) {
                    event_data['created_by'] = res.created_by;
                } else {
                    event_data['created_by'] = null;
                }

                if (res.host_user) {
                    event_data['host_user'] = res.host_user;
                } else {
                    event_data['host_user'] = null;
                }

                fillEventData(event_data, event);

                if (event_data['custom_address']) {
                    $("#event-defined-location-panel").slideUp();
                    $("#event-custom-location-panel").slideDown();

                }

                if (!event.editable) {
                    $('form#schedule-form fieldset#main_fieldset').attr('disabled', true);
                    $('form#schedule-form fieldset#main_fieldset .schedule-select2').prop('disabled', true);
                    $('#submit-btn').hide();

                } else {
                    $('form#schedule-form fieldset#main_fieldset').removeAttr('disabled');
                    $('#submit-btn').show();
                }

                setEventFormAccess(true);
                setMeetingRoomHeadquarter();

                $('#addScheduleFormModal').modal('show');
            }
        }
    });
}

function moveEvent(url, event, revertFunc) {

    swal({
        title: "Czy na pewno zmienić termin zdarzenia?",
        type: 'warning',
        showCancelButton: true,
        confirmButtonText: "Tak, zmień!",
        confirmButtonColor: "#DD6B55",
        cancelButtonText: "Nie"
    }).then((result) => {
        if (result.value) {
            $.ajax(url, {
                dataType: 'json',
                method: 'POST',
                data: {'id': event.id, 'start': event.start.format(), 'end': event.end.format(), 'csrfmiddlewaretoken': csrf_token},
                success: function (res) {
                },
                error: function (res) {
                    if (typeof revertFunc === 'function') {
                        revertFunc();
                    }
                    swal({
                        title: "Błąd!",
                        text: res.responseJSON.errmsg,
                        type: 'error',
                        confirmButtonText: "ok"
                    });
                },
                complete: function () {
                    $("#calendar").fullCalendar('refetchEvents');
                }
            });
        } else {
            $("#calendar").fullCalendar('refetchEvents');
        }
    });
}

function confirmEvent(id_schedule, id_user, e) {
    swal({
        title: "Czy na pewno potwierdzić uczestnictwo?",
        type: 'warning',
        showCancelButton: true,
        confirmButtonText: "Tak, potwierdź!",
        confirmButtonColor: "#DD6B55",
        cancelButtonText: "Nie",
        closeOnConfirm: false
    }).then((result) => {
        if (result.value) {
            $.ajax('/schedule/schedule-participant-confirm/', {
                method: 'POST',
                data: {id_schedule: id_schedule, id_user: id_user, csrfmiddlewaretoken: window.csrf_token},
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

                    if (e) {
                        e.switchClass('fa-times', 'fa-check');
                        e.parents('tr').find('input[name="users-invited_users_confirmed"]').val(1);
                    }

                    $("#calendar").fullCalendar('refetchEvents');
                    swal('Uczestnictwo zostało potwierdzone!', '', 'success');
                }
            });
        }
    });
}

function rejectEvent(id_schedule, id_user, e) {
    swal({
        title: "Czy na pewno anulować uczestnictwo?",
        type: 'warning',
        showCancelButton: true,
        confirmButtonText: "Tak, anuluj!",
        confirmButtonColor: "#DD6B55",
        cancelButtonText: "Nie",
        closeOnConfirm: false
    }, function () {

        $.ajax('/schedule/schedule-participant-reject/', {
            method: 'POST',
            data: {id_schedule: id_schedule, id_user: id_user, csrfmiddlewaretoken: window.csrf_token},
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
                    if (e) {
                        e.switchClass('fa-check', 'fa-times');
                        e.parents('tr').find('input[name="users-invited_users_confirmed"]').val(0);
                    }
                    $("#calendar").fullCalendar('refetchEvents');
                    swal('Uczestnictwo zostało anulowane!', '', 'success');
                }
            }
        });
    });
}

function closeEvent(id_schedule, id_user) {
    swal({
        title: "Czy na pewno zamknąć zdarzenie?",
        type: 'warning',
        showCancelButton: true,
        confirmButtonText: "Tak, zamknij!",
        confirmButtonColor: "#DD6B55",
        cancelButtonText: "Nie",
        closeOnConfirm: false
    }, function () {

        $.ajax('/schedule/schedule-close/', {
            method: 'POST',
            data: {id_schedule: id_schedule, id_user: id_user, csrfmiddlewaretoken: window.csrf_token},
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
                    $("#calendar").fullCalendar('refetchEvents');
                    swal('Zdarzenie zostało zamknięte!', '', 'success');

                }
            }
        });
    });
}

function statusEvent(id_schedule, id_user, status, toggle, callback) {
    // swal({
    //     title: "Czy na pewno kontynuować?",
    //     type: 'warning',
    //     showCancelButton: true,
    //     confirmButtonText: "Tak!",
    //     confirmButtonColor: "#DD6B55",
    //     cancelButtonText: "Nie",
    //     closeOnConfirm: false
    // }, function () {

    $.ajax('/schedule/schedule-status/', {
        method: 'POST',
        data: {id_schedule: id_schedule, id_user: id_user, status: status, csrfmiddlewaretoken: window.csrf_token},
        complete: function (xhr) {
            var resp = xhr.responseJSON;
            if (resp.status !== "OK") {
                swal({
                    title: "Błąd!",
                    text: resp.errmsg,
                    type: 'error',
                    confirmButtonText: "ok"
                });
            } else {
                $("#calendar").fullCalendar('refetchEvents');
                if (toggle) {
                    $("#addScheduleFormModal").modal('toggle');
                }
                if (callback) {
                    callback();
                }
                swal('Zmiana wykonana pomyślnie!', '', 'success');
            }
        }
    });
    // });
}

function deleteEvent(id) {
    swal({
        title: "Czy na pewno usunąć zdarzenie?",
        type: 'warning',
        showCancelButton: true,
        confirmButtonText: "Tak, usuń!",
        confirmButtonColor: "#DD6B55",
        cancelButtonText: "Nie",
        closeOnConfirm: false
    }, function () {

        $.ajax('/schedule/schedule-delete/', {
            method: 'POST',
            data: {'id': id, 'csrfmiddlewaretoken': window.csrf_token},
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
                    $('#calendar').fullCalendar('removeEvents', id);
                    swal('Zdarzenie zostało usunięte!', '', 'success');

                }
            }
        });
    });
}

function toggleParticipantConfirmation(e) {

    var id_user = e.closest('tr').data('id');
    var id_schedule = $("form#schedule-form #id").val();
    var confirm = e.hasClass('fa-times');

    if (confirm) {
        confirmEvent(id_schedule, id_user, e);
    } else {
        rejectEvent(id_schedule, id_user, e);
    }
}


