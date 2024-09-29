function create_post() {
    let participantList = [];
    let participants = $('form#schedule-form #id_schedule-mode').val() === 'basic' ? window.participantBasic : window.participantAdvanced;
    participantList = participants.participant.getList();
    // todo: drut

    if ($('form#schedule-form #id_schedule-type option:selected').data('single_person') === 'True') {
        participantList = [{id: $("#id_schedule-single_person_").val(), parent: ''}];
    }

    console.log(JSON.stringify(participantList));

    $("#id_schedule-participants_json").val(JSON.stringify(participantList));

    $.ajax({
        url: "/schedule/schedule-add/",
        type: "POST",
        data: $("form#schedule-form").serialize(),
        success: function () {
            resetCalendarMode();
            $('#calendar').fullCalendar('refetchEvents');
            $('#addScheduleFormModal').modal('toggle');
        },
        error: function (response) {

            let resp = response.responseJSON;

            Alert.error('Błąd', resp.errmsg);

            $(".btn-success").prop('disabled', false);

            if (typeof resp.form_errors !== "undefined") {
                if (typeof resp.form_errors.ScheduleForm !== "undefined") {

                    $.each(resp.form_errors.ScheduleForm, function (i, e) {

                        let formGroup = $('#id_schedule-' + i).closest('div.form-group');
                        formGroup.addClass('form-field-error');

                        let errors = '';
                        $.each(e, function (i, e) {
                            errors += '<li>' + e + '</li>';
                        });

                        formGroup.append('<ul class="errorlist">' + errors + '<ul>');

                        let error_list = $('#addScheduleFormModal').find('#error_list');
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

                if (res.notes) {
                    event_data['notes'] = $.parseJSON(res.notes);
                } else {
                    event_data['notes'] = null;
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
                    $('form#schedule-form fieldset#main_fieldset').attr('disabled', true); // TODO: Błąd: blokuje cały collapse. Zmienić niezwłocznie!!!!

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
    Alert.questionWarning("Czy na pewno zmienić termin zdarzenia?", '',
        () => {
            $.ajax(url, {
                method: 'POST',
                data: {'id': event.id, 'start': event.start.format(), 'end': event.end.format(), 'csrfmiddlewaretoken': csrf_token},

                success: () => {

                },
                error: (res) => {
                    if (typeof revertFunc === 'function') {
                        revertFunc();
                    }
                    Alert.error("Błąd!", res.responseJSON.errmsg);
                },
                complete: () => {
                    $("#calendar").fullCalendar('refetchEvents');
                }
            })
        },
        '',
        () => {
            $("#calendar").fullCalendar('refetchEvents');
        })

    // Swal({
    //     title: "Czy na pewno zmienić termin zdarzenia?",
    //     type: 'warning',
    //     showCancelButton: true,
    //     confirmButtonText: "Tak, zmień!",
    //     confirmButtonColor: "#DD6B55",
    //     cancelButtonText: "Nie"
    // }).then((result) => {
    //     if (result.value) {
    //         $.ajax(url, {
    //             dataType: 'json',
    //             method: 'POST',
    //             data: {'id': event.id, 'start': event.start.format(), 'end': event.end.format(), 'csrfmiddlewaretoken': csrf_token},
    //             success: function (res) {
    //             },
    //             error: function (res) {
    //                 if (typeof revertFunc === 'function') {
    //                     revertFunc();
    //                 }
    //                 swal({
    //                     title: "Błąd!",
    //                     text: res.responseJSON.errmsg,
    //                     type: 'error',
    //                     confirmButtonText: "ok"
    //                 });
    //             },
    //             complete: function () {
    //                 $("#calendar").fullCalendar('refetchEvents');
    //             }
    //         });
    //     } else {
    //         $("#calendar").fullCalendar('refetchEvents');
    //     }
    // });
}

function confirmEvent(id_schedule, id_user, e) {
    swal({
        title: "Czy na pewno potwierdzić uczestnictwo?",
        type: 'warning',
        showCancelButton: true,
        confirmButtonText: "Tak, potwierdź!",
        confirmButtonColor: "#DD6B55",
        cancelButtonText: "Nie"
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

    Alert.questionWarning(
        "Czy na pewno anulować uczestnictwo?",
        '',
        () => {

            ajaxCall({
                    url: '/schedule/schedule-participant-reject/',
                    method: 'POST',
                    data: {id_schedule: id_schedule, id_user: id_user, csrfmiddlewaretoken: window.csrf_token}
                },
                (xhr) => {
                    let resp = xhr.responseJSON;
                    swal({
                        title: "Błąd!",
                        text: resp.message,
                        type: 'error',
                        confirmButtonText: "ok"
                    });
                }, () => {
                    if (e) {
                        e.switchClass('fa-check', 'fa-times');
                        e.parents('tr').find('input[name="users-invited_users_confirmed"]').val(0);
                    }
                    $("#calendar").fullCalendar('refetchEvents');
                    Alert.info('Uczestnictwo zostało anulowane!');
                })
        });
}

function closeEvent(id_schedule, id_user) {

    Alert.questionWarning(
        "Czy na pewno zamknąć zdarzenie?",
        '',
        () => {
            ajaxCall({
                    url: '/schedule/schedule-close/',
                    method: 'POST',
                    data: {id_schedule: id_schedule, id_user: id_user, csrfmiddlewaretoken: window.csrf_token}
                },
                (xhr) => {
                    var resp = xhr.responseJSON;
                    swal({
                        title: "Błąd!",
                        text: resp.message,
                        type: 'error',
                        confirmButtonText: "ok"
                    });
                },
                () => {
                    $("#calendar").fullCalendar('refetchEvents');
                    Alert.info('Zdarzenie zostało zamknięte!');
                });
        });
}

function statusEvent(id_schedule, id_user, status, toggle, callback) {

    $.ajax('/schedule/schedule-status/', {
        method: 'POST',
        data: {
            id_schedule: id_schedule,
            id_user: id_user,
            status: status,
            csrfmiddlewaretoken: window.csrf_token,
            note: $("#schedule-form #id_message-text").val()
        },
        complete: function (xhr) {
            let resp = xhr.responseJSON;
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
                if (callback && typeof callback === 'function') {
                    callback();
                }
            }
        }
    });
}

function deleteEvent(id) {
    Alert.questionWarning(
        "Czy na pewno usunąć zdarzenie?",
        '',
        () => {
            $.ajax('/schedule/schedule-delete/', {
                method: 'POST',
                data: {'id': id, 'csrfmiddlewaretoken': window.csrf_token},
                complete: function (xhr) {
                    let resp = xhr.responseJSON;
                    if (resp.status != "OK") {
                        Alert.error("Błąd!", resp.message);
                    } else {
                        $('#calendar').fullCalendar('removeEvents', id);
                        Alert.info('Zdarzenie zostało usunięte!');
                    }
                }
            });
        });
}

function toggleParticipantConfirmation(e) {

    let id_user = e.closest('tr').data('id');
    let id_schedule = $("form#schedule-form #id").val();
    let confirm = e.hasClass('fa-times');

    if (confirm) {
        confirmEvent(id_schedule, id_user, e);
    } else {
        rejectEvent(id_schedule, id_user, e);
    }
}


