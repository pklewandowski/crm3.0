/**
 * Client side utitlities functions
 * @param id
 */

let gXhr = null;

function resetEventForm(id, mode, wholeDayOnly) {


    $('#add_schedule_form_container').html($('template#form_main_template').html());

    if (wholeDayOnly) {
        $("form#schedule-form #wholeDayOnly").val("True");
    }

    $("#confirmEventWithNoteModal #eventNote").val(null);

    getFormContent(mode);
    initMap();

    if (mode === 'advanced') {
        $('#mode_toggle_btn').hide();
    }
}

function fillParticipantList(u) {

    var participant_type_dict = {'L': 'Prowadzący', 'P': 'Uczestnik'};
    var tmpl = $("#event-user-list-row-template").html();

    tmpl = tmpl.replace(/__user_id__/g, u.id);
    tmpl = tmpl.replace(/__user_name__/g, u.first_name + ' ' + u.last_name);
    tmpl = tmpl.replace('__user_phone_one__', u.phone_one);
    tmpl = tmpl.replace('__user_phone_two__', u.phone_two);
    tmpl = tmpl.replace('__user_email__', u.email);
    tmpl = tmpl.replace('__participant_type_label__', participant_type_dict[u.participant_type]);
    tmpl = tmpl.replace('__participant_type__', u.participant_type);
    tmpl = tmpl.replace(/__user_confirmation__/g, u.confirmed ? 'check' : 'times');
    tmpl = tmpl.replace(/__user_confirmed__/g, u.confirmed ? '1' : '0');
    tmpl = tmpl.replace(/__active__/g, u.active ? 'active' : '');
    tmpl = tmpl.replace(/__opacity__/g, u.active ? '' : 'opacity40');
    tmpl = tmpl.replace(/__current_participant__/g, (parseInt(u.id) === parseInt(window.id_current_user)) ? 'current-participant' : '');
    tmpl = tmpl.replace('__exclusive_participant_mode_checked__', u.exclusive_participant_mode ? 'checked' : '');
    tmpl = tmpl.replace('__exclusive_participant_mode_value__', u.exclusive_participant_mode ? '1' : '0');

    return tmpl;
}

function fillCustomLocationAddress(c) {
    $('form#schedule-form #id_address-street').val(c.street);
    $('form#schedule-form #id_address-street_no').val(c.street_no);
    $('form#schedule-form #id_address-apartment_no').val(c.apartment_no);
    $('form#schedule-form #id_address-city').val(c.city);
    $('form#schedule-form #id_address-province').val(c.province);
    $('form#schedule-form #id_address-post_code').val(c.post_code);
    $('form#schedule-form #id_address-country').val(c.country);
    $('form#schedule-form #id_address-email').val(c.email);
    $('form#schedule-form #id_address-phone').val(c.phone);
}

function convertHourToMinutes(mmt) {
    if (!moment.isMoment(mmt)) {
        return 0;
    }
    var hh = mmt.get('hour');
    var mm = mmt.get('minute');

    return hh * 60 + mm;
}

function fillEventData(event_data, event) {

    $("#event-user-list-row-table tbody").html(null);

    let e = event_data['schedule'].fields;
    let hun = event_data['host_user'];

    let t = event_data['event_type'];
    let c = event_data['custom_address'] ? event_data['custom_address'].fields : null;
    let m = event_data['meeting_room'] ? event_data['meeting_room'] : null;
    let u = event_data['users'];
    let ms = event_data['notes'];

    $('form#schedule-form #id').val(event.id);
    $('form#schedule-form #editable').val(event.editable);
    $('form#schedule-form #id_created_by').val(e.created_by);
    $('form#schedule-form #status').val(e.status);
    $('form#schedule-form #created_by-container h5 span').text(event_data['created_by']);

    let newOption = new Option(hun, e.host_user, true, true);
    $('#id_schedule-host_user_').append(newOption).trigger('change');

    $('form#schedule-form #id_schedule-host_user option[value="' + e.host_user + '"]').attr('selected', true);
    $('form#schedule-form #id_schedule-type option[value="' + t.pk + '"]').attr('selected', true);
    $('form#schedule-form #id_schedule-type option').not(':selected').attr('disabled', 'disabled');

    $('form#schedule-form #id_schedule-title').val(e.title);
    $('form#schedule-form #id_schedule-meeting_room option[value="' + e.meeting_room + '"]').attr('selected', true);
    $('form#schedule-form #id_schedule-start_date').data('DateTimePicker').date(e.start_date); //val(moment(e.start_date).format('YYYY-MM-DD HH:mm'));
    $('form#schedule-form #id_schedule-end_date').data('DateTimePicker').date(e.end_date); //val(moment(e.end_date).format('YYYY-MM-DD HH:mm'));
    $('#id_schedule-end_date').data("DateTimePicker").minDate(moment(e.start_date).add(15, 'minutes').format('YYYY-MM-DD HH:mm'));
    $('form#schedule-form #id_schedule-description').val(e.description);


    if (m) {
        $('form#schedule-form #id_schedule-headquarter option[value="' + m.fields.headquarter + '"]').prop('selected', true);
        setMeetingRoom(m.pk);
    }
    else if (c) {
        fillCustomLocationAddress(c);
    }

    if (u) {
        // if (event.data.single_person) {
        //     let user = u[0];
        //     $("form#schedule-form #id_schedule-single_person_").append(new Option(`${user.first_name} ${user.last_name}`, user.id));
        // }
        // $.each(u, function (i, e) {
        //
        //     e['active'] = parseInt(e.id) === parseInt(window.id_current_user) || window.permissions.schedule_toggle_confirm_all;
        //     $("#event-user-list-row-table").find("tbody").append(fillParticipantList(e));
        // });

        window.participantAdvanced.participant.load(u);
    }

    if (ms) {
        $.each(ms, function (i, e) {

            let msContainer = $('#event-message-container').find('ul#event_notes');
            msContainer.append('<li><div class="event-message-header">' + e.created_date + ' ' + e.user + '</div>' +
                '<div class="event-message-text">' + e.text + '</div></li>');
        });
    }
}

function fillAddressForm(place, guide, addressContainerId) {

    var form = [];

    for (var i = 0; i < place.address_components.length; i++) {
        var addressType = place.address_components[i].types[0];
        if (guide[addressType]) {
            var val = place.address_components[i][guide[addressType]];
            form[addressType] = val;
        }
    }

    form['lat'] = place.geometry.location.lat();
    form['lng'] = place.geometry.location.lng();

    $("#id_address-street").val(form['route']);
    $("#id_address-street_no").val(form['street_number']);
    $("#id_address-city").val(form['administrative_area_level_2']);
    $("#id_address-province").val(form['administrative_area_level_1']);
    $("#id_address-country").val(form['country']);
    $("#id_address-post_code").val(form['postal_code']);

    return form;
}

function setAvailableMeetingRooms(rooms) {

    $('.meeting-room-btn').removeClass('disabled');
    $('.meeting-room-btn input[type=radio]').removeAttr('disabled');

    $.each($('form#schedule-form input:radio[name="schedule-meeting_room"]'), function (i, e) {
        if ($.inArray(parseInt($(e).val()), rooms) === -1) {
            disableMeetingRoom($(e).val());
        }
    });
}

function setMeetingRoomHeadquarter() {
    let hdq = $("form#schedule-form #id_schedule-headquarter").val();
    $(".meeting-room-select-buttons .headquarter-meeting_room-container").hide();
    $('.meeting-room-select-buttons #headquarter_' + hdq).show();
}

function getAvailableMeetingRooms(start, end) {
    if (!start || !end) {
        return
    }

    $.ajax({
        url: urlGetAvailableMeetingRooms,
        method: 'post',
        data: {start: start, end: end, exclude: $("form#schedule-form #id").val()},
    }).done(function (res) {
        setAvailableMeetingRooms(res.data);

    }).fail(function (response) {
        var res = response.responseJSON;
        swal(res.errmsg, '', 'warning');
    })
}

function _setDefaultEventType() {
    "use strict";
    let scheduleForm = $('form#schedule-form');
    scheduleForm.find('#id_schedule-type option[data-is_default="False"]').remove();
}

function setInitialData(start, end) {
    let scheduleForm = $('form#schedule-form');
    if (scheduleForm.find("#wholeDayOnly").val() !== 'True') {
        _setDefaultEventType();
    }

    scheduleForm.find("#mode").val("basic");

    scheduleForm.find('#id_schedule-host_user option[value="' + gUser.id + '"]').prop('selected', true);
    let eventType = scheduleForm.find('#id_schedule-type option:selected');

    scheduleForm.find("#id_schedule-title").val(eventType.data('default_title') ? eventType.data('default_title') : 'Spotkanie');
    $("#created_by-container").find('span').text(gUser.firstName + ' ' + gUser.lastName);

    $('form#schedule-form input#id_' + g_form_prefix + '-start_date').data("DateTimePicker").date(start.format('YYYY-MM-DD HH:mm'));
    $('form#schedule-form input#id_' + g_form_prefix + '-end_date').data("DateTimePicker").date(end.format('YYYY-MM-DD HH:mm'));
    // $('form#schedule-form input#id_' + g_form_prefix + '-start_date').val(start.format('YYYY-MM-DD HH:mm'));
    // $('form#schedule-form input#id_' + g_form_prefix + '-end_date').val(end.format('YYYY-MM-DD HH:mm'));


    $('#id_schedule-end_date').data("DateTimePicker").minDate(moment.utc(start.clone().add(15, 'minutes')));

    setMeetingRoomHeadquarter();
}

/**
 * @function setEventFormAccess
 * @description
 * Ustawia widoczność, zależność itp. pól dla danego typu zdarzenia.
 * Pole is_schedule-type zawiera metadane, na podstawie których są ustawiane pola formularza.
 * Metadane ustawiane są w partialu schedule/partial/_modal_event_data_partial.html
 * @param init
 */
function setEventFormAccess(init) {

    let schedule_form = $('form#schedule-form');
    let e = schedule_form.find("#id_schedule-type option:selected");

    if (!init) {
        schedule_form.find('#id_schedule-title').val((e.data("default_title") !== null && e.data("default_title") !== '' ) ? e.data("default_title") : e.val());
    }

    let serviceCtrl = schedule_form.find("#id_schedule-service");

    if (e.data("event_kind") !== 'U') {
        // serviceCtrl.find("option:selected").removeAttr("selected");
        serviceCtrl.closest('.form-group').hide(200);
        toggle_form_elements('#eventProductRetailCollapse', false);
        schedule_form.find("#event_product_retail_panel").hide(200);
        schedule_form.find("#product_retail_container").hide(200);

    }
    else {
        serviceCtrl.closest('.form-group').show(200);
        toggle_form_elements('#eventProductRetailCollapse', true);
        schedule_form.find("#event_product_retail_panel").show(200);
        schedule_form.find("#product_retail_container").show(200);
    }

    if (e.data("title_required") === 'True') {
        schedule_form.find('#id_schedule-title').removeAttr('readonly');
    }

    if (e.data("location_required") === 'False') {
        clear_form_elements('#eventLocationCollapse');
        toggle_form_elements('#eventLocationCollapse', false);
        schedule_form.find("#event_location_panel").hide(200);

    } else {
        toggle_form_elements("#eventLocationCollapse", true);
        schedule_form.find("#event_location_panel").show(200);
    }

    if (e.data("single_person") === 'True') {
        schedule_form.find("#event-user-list-row-table tbody").html(null);
        schedule_form.find("#search-box").attr('disabled', true);
        schedule_form.find("#event_users_panel").hide();
        schedule_form.find("#id_schedule-single_person_").closest(".form-group").show(200)
    } else {
        schedule_form.find("#search-box").removeAttr('disabled');
        schedule_form.find("#event_users_panel").show();
        schedule_form.find("#id_schedule-single_person_").closest(".form-group").hide(200)
    }

    if (schedule_form.find('#id').val()) {

        schedule_form.find('#id_schedule-is_cyclical').closest('.form-group').remove();

        // TODO: poprawić, żebuy było dobrze. teraz nawet ten, kto nie ma uprawnień do edycji może aktywować zdarzenie
        if (schedule_form.find("#status").val() === 'AN') {
            schedule_form.find("#activate-btn").show();
            schedule_form.find("#cancelMenu").hide();
        }
        else {
            schedule_form.find("#activate-btn").hide();
        }

        if (schedule_form.find('#editable').val() === 'true') {

            schedule_form.find("#submit-btn").show();
            schedule_form.find("#cancel-btn").show();
            schedule_form.find("#cancel_and_set-btn").show();
            schedule_form.find("#close-btn").show();
            schedule_form.find("#closeAndSetBtn").show();
            schedule_form.find("#delete-btn").show();

            let endDt = moment(schedule_form.find("#id_schedule-end_date").val() + $("form#schedule-form #start_date").text(), 'YYYY-MM-DDHH:mm').toDate();

            if (endDt > moment()) {
                schedule_form.find("#close-btn").hide();
                schedule_form.find("#closeAndSetBtn").hide();
            }
        }
        else {
            schedule_form.find("#submit-btn").hide();
            schedule_form.find("#cancel-btn").hide();
            schedule_form.find("#cancel_and_set-btn").hide();
            schedule_form.find("#close-btn").hide();
            schedule_form.find("#closeAndSetBtn").hide();
            schedule_form.find("#delete-btn").hide();
            schedule_form.find("#saveMenu").hide();
            schedule_form.find("#cancelMenu").hide();

            //schedule_form.find("#activate-btn").hide();
        }
    }
    else {
        schedule_form.find("#cancelMenu").hide();
        schedule_form.find("#submit-btn").show();
        schedule_form.find("#cancel-btn").hide();
        schedule_form.find("#cancel_and_set-btn").hide();
        schedule_form.find("#close-btn").hide();
        schedule_form.find("#closeAndSetBtn").hide();
        schedule_form.find("#delete-btn").hide();
        schedule_form.find("#activate-btn").hide();
    }


    // {#                <button id="close-btn" type="button" class="btn btn-primary">Zakończ...</button>#}
    //
    //             {#                <div class="btn-group">#}
    //             {#                    <button id="cancel-btn" type="button" class="btn btn-default">Anuluj...</button>#}
    //             {#                    <button id="cancel_and_set-btn" type="button" class="btn btn-default">Anuluj i umów ponownie...</button>#}
    //             {#                </div>#}
    //             {##}
    //             {#                <button id="delete-btn" type="button" class="btn btn-danger">Usuń...</button>#}
    //
    //             {#                <button id="activate-btn" type="button" class="pad-l btn btn-success">Aktywuj...</button>#}
    //             {#                <button id="submit-btn" type="button" class="pad-l btn btn-success">Zapisz...</button>#}

    function setConfirmAlertActionButtons() {
        "use strict";
        let schedule_form = $('form#schedule-form');
        let saveHtml = '';
        let cancelHtml = '';

        if (schedule_form.find('#id').val()) {

            if (schedule_form.find('#editable').val() === 'true') {

                saveHtml += gActionBtn.submit;
                cancelHtml += gActionBtn.delete + gActionBtn.deleteAndSet;

                let endDt = moment(schedule_form.find("#id_schedule-end_date").val() + $("form#schedule-form #start_date").text(), 'YYYY-MM-DDHH:mm').toDate();

                if (endDt <= moment()) {
                    saveHtml += gActionBtn.close;
                }
            }
            else {
                schedule_form.find("#saveMenu").hide();
                schedule_form.find("#cancelMenu").hide();

                //schedule_form.find("#activate-btn").hide();
            }

        }
        else {
            schedule_form.find("#cancelMenu").hide();
            cancelHtml = '';
            saveHtml += gActionBtn.submit;
        }

        return {save: saveHtml, cancel: cancelHtml}


        // let template = $('#actionButtonsTemplate');
        // let content = template.prop('content');
        // let btn = $(content).find("#submit-btn");
    }

    let actionHtml = setConfirmAlertActionButtons();
    gSaveActionBtnHtml = actionHtml.save;
    gCancelActionBtnHtml = actionHtml.cancel;

}

function triggerAction(html) {
    "use strict";
    swal({
        title: 'Wybierz akcję',
        html: html,
        type: 'success',
        showCloseButton: true,
        showConfirmButton: false
    }).then((result) => {
        swal.close();
    })
}

/**
 * @function eventDataDecode
 * @description
 * Dekoduje ajaxa dla eventów, przychodzącego z serwera. Dla zmniejszenia ilości przesyłanych danych (optymalizacja)
 * dane przychodzą w formie array-a, a nie dicta. Funkcja zamienia array-a na dicta (human friendly :)
 * potrzebnego dla eventu calendar-control.js/renderEvent kalendarza
 * @param ev
 * @returns {{}}
 */
function eventDataDecode(ev) {
    let guide = ['id', 'id_cyclical', 'is_cyclical', 'title', 'start', 'end', 'color', 'viewable', 'editable', 'details_viewable', 'data'];
    let dataGuide = ['single_person', 'whole_day', 'confirmed', 'host_user', 'address', 'resizable', 'status', 'invited_users'];
    let userGuide = ['pk', 'first_name', 'last_name', 'phone_one', 'phone_two', 'email', '_edit_link', 'product_retail'];
    let productRetailGuide = ['product', 'quantity', 'unit_price', 'payment_type'];

    function _setUser(el) {
        let user = {};
        $.each(el, function (i, e) {
            switch (userGuide[i]) {
                case 'product_retail':
                    let pr = [];
                    $.each(e, function (i1, e1) {
                        let _pr = {};
                        $.each(e1, function (i2, e2) {
                            _pr[productRetailGuide[i2]] = e2;
                        });
                        pr.push(_pr)
                    });
                    user[userGuide[i]] = pr;
                    break;
                default:
                    user[userGuide[i]] = e;
            }
        });
        return user;
    }

    function _setInvitedUsers(el) {
        let invitedUsers = [];
        $.each(el, function (i, e) {
            invitedUsers.push(_setUser(e))
        });
        return invitedUsers;
    }

    let _event = {};

    $.each(ev, function (i, e) {
        switch (guide[i]) {
            case 'data':
                let _ev = {};

                $.each(e, function (_i, _e) {

                    switch (dataGuide[_i]) {
                        case 'host_user':
                            _ev[dataGuide[_i]] = _setUser(_e);
                            break;

                        case 'invited_users':
                            _ev[dataGuide[_i]] = _setInvitedUsers(_e);
                            break;

                        default:
                            _ev[dataGuide[_i]] = _e;
                            break;
                    }
                });

                _event['data'] = _ev;
                break;

            default:
                _event[guide[i]] = e;
                break;
        }
    });

    if (_event.data.whole_day) {
        _event['allDay'] = true;
        _event['stick'] = true;
        _event['start'] = _event['start'].substr(0, 10);
        _event['end'] = _event['end'].substr(0, 10);
    }
    return _event;
}

function getHeadquarters() {
    // let hdq = [];
    //
    // $.each($("#user_headquerters_list").find('input[type=checkbox]:checked'), function (i, e) {
    //     let _e = $(e);
    //     hdq.push(_e.val());
    // });
    // return hdq;
    return $("#user_headquarters_list").val()
}

function getEvents(start, end, callback) {

    if (calendar_mode === 'dates') {
        callback(availableDates);
        return;
    }

    let data = {
        start: start.format('YYYY-MM-DD'),
        end: end.format('YYYY-MM-DD'),
        id_user: window.id_user,
        csrfmiddlewaretoken: window.csrf_token,
        calendar_mode: calendar_mode,
        filter: JSON.stringify(gFilter),
        headquarter: getHeadquarters()
    };

    if (gXhr) {
        gXhr.abort();
    }
    gXhr = $.ajax({
        url: "/schedule/calendar/get-events/",
        type: "POST",
        data: data,
        success: function (res) {
            let events = [];
            $.each(res.events, function (i, e) {
                let _event = eventDataDecode(e);
                // TODO: zmiana: wykorzystamy slot AllDay w kalendarzu.

                // _event.start=new Date('2019-02-25');
                // _event.end=new Date('2019-02-28');
                //if (_event.data.whole_day) {

                // let days = moment(new Date(_event.end)).diff(moment(new Date(_event.start)), 'days');
                // let start = moment(moment(new Date(_event.start)).format('YYYY-MM-DD'));
                // for (i = 0; i <= days; i++) {
                //     ev = {};
                //     Object.assign(ev, _event);
                //     ev.start = start.format('YYYY-MM-DD') + 'T09:00:00';
                //     ev.end = start.format('YYYY-MM-DD') + 'T19:00:00';
                //     if (i !== 0) {
                //         ev.editable = false;
                //         ev.details_viewable = false;
                //         ev.title = ev.title + "-cd.";
                //     }
                //     start.add(1, 'days');
                //     events.push(ev);
                // }
                // }
                // else {
                events.push(_event);
                // }
            });
            callback(events);
        },
        error: function (xhr, errmsg, err) {
            if (xhr.statusText === 'abort') {
                return;
            }
            swal(errmsg, '', 'error');
        },
        complete: function () {
        }
    });
}

function getAvailableDates() {
    $.ajax({
        type: 'post',
        url: '/schedule/get-available-date/',
        data: {
            employee_id: $("#id_filter-employee").val(),
            user_id: $("#id_filter-user").val(),
            meeting_room_id: $("#id_filter-meeting_room").val(),
            from_date: $("#id_filter-from_date").val(),
            from_hour: $("#id_filter-from_hour").val(),
            to_hour: $("#id_filter-to_hour").val(),
            min_duration: $("#id_filter-min_duration").val()
        },
        error: function (response, textStatus, errorThrown) {
            if (response.statusText === 'abort') {
                return;
            }

            if (response.statusText === 'abort') {
                return;
            }
            swal(response.errmsg, '', 'error');
        }
    }).done(function (response) {
        let rLength = response.ranges.length;

        availableDates = [];

        if (!rLength) {
            swal('Nie ma możliwości ustalenia terminu dla wskazanych kryteriów', '', 'info');
            calendar_mode = 'event';
            $("#calendar").fullCalendar('refetchEvents');
            $("#available_date_reset_btn").hide();
            return;
        }

        $.each(response.ranges, function (i, e) {

            event = {
                'start': e.start,
                'end': e.end,
                'color': i === (rLength - 1) ? '#4c8e05' : '#7ce40c',
                'rendering': 'background'
            }
            availableDates.push(event);
        });

        calendar_mode = 'dates';
        gCalendarControl.fullCalendar('gotoDate', availableDates[0].start);
        gCalendarControl.fullCalendar('refetchEvents');

        $("#available_date_reset_btn").show();

        let modal = $('#available_date_modal');
        let ul = modal.find('#available_date_list');

        ul.html(null);
        $.each(response.ranges, function (i, e) {
            ul.append('<li><a href="#" data-date="' + e.start.substr(0, 10) + '">' + e.start + ' - ' + e.end + '</a></li>');
        });
        modal.modal();
    });
}

function getFormContent(mode) {
    let scheduleForm = $('form#schedule-form');
    let startDate = scheduleForm.find("#id_schedule-start_date").val();
    let endDate = scheduleForm.find("#id_schedule-end_date").val();
    let type = scheduleForm.find('#id_schedule-type option:selected').val();
    let title = scheduleForm.find('#id_schedule-title').val();
    let hostUser = scheduleForm.find('#id_schedule-host_user').val();
    let meetingRoom = scheduleForm.find('input[name="schedule-meeting_room"]:checked').val();
    let service = scheduleForm.find('#id_schedule-service').val();
    let headquarter = scheduleForm.find('#id_schedule-headquarter').val();
    // let product_retail_container_basic = scheduleForm.find('#product_retail_container_basic');
    // let product_retail_container_advanced = scheduleForm.find('#product_retail_container_advanced');
    // let product_retail_container = scheduleForm.find('#product_retail_container');

    function _setTemplate() {
        if (mode === 'basic') {
            $('#add_schedule_form_container').find('#form_content').html($('template#form_basic_template').html());
            let opt = new Option(gUser.firstName + " " + gUser.lastName, gUser.id);
            $("#id_schedule-employee_").append(opt);
        }
        else if (mode === 'advanced') {
            $('#add_schedule_form_container').find('#form_content').html($('template#form_advanced_template').html());
            $('#cyclicalSettingsModal').html($('#cyclicalSettingsTemplate').html());
            let opt = new Option(gUser.firstName + " " + gUser.lastName, gUser.id);
            $("#id_schedule-host_user_").append(opt);
            // product_retail_container.appendTo('#product_retail_container_advanced')
        }

        if (scheduleForm.find("#wholeDayOnly").val() === 'True') {
            $("form#schedule-form #wholeDayOnly").val("True");
            $('form#schedule-form #id_schedule-type option[data-whole_day_event="False"]').remove();
        }
        else {
            $('form#schedule-form #id_schedule-type option[data-whole_day_event="True"]').remove();
        }

        setCalendarDatetimePicker($('form#schedule-form input#id_schedule-start_date'));
        setCalendarDatetimePicker($('form#schedule-form input#id_schedule-end_date'));

        $('#id_schedule-start_date').datetimepicker().on('dp.change', function (e) {

            let minDt = e.date.clone().add(15, 'minutes');
            let end = $('#id_schedule-end_date').data("DateTimePicker").date();

            $('#id_schedule-end_date').data("DateTimePicker").minDate(minDt.format('YYYY-MM-DD HH:mm'));

            if (!end || (end <= minDt)) {
                $('#id_schedule-end_date').data("DateTimePicker").date(minDt.format('YYYY-MM-DD HH:mm'));
            }
            getAvailableMeetingRooms($('form#schedule-form #id_schedule-start_date').val(), $('form#schedule-form #id_schedule-end_date').val());
        });

        $('#id_schedule-end_date').datetimepicker().on('dp.change', function (e) {
            getAvailableMeetingRooms($('form#schedule-form #id_schedule-start_date').val(), $('form#schedule-form #id_schedule-end_date').val());
        });



        let allowMultipleUserChoice = true;
        if (mode === 'basic' && allowMultipleUserChoice) {
            window.participantBasic = new ParticipantControlBasic('participantContainer');
        }

        if (mode === 'advanced') {
            window.participantAdvanced = new ParticipantControlAdvanced('participantContainer');

            $("#id_schedule-host_user_").select2({
                theme: 'bootstrap',
                ajax: {
                    method: 'post',
                    url: '/schedule/get-employees-for-meeting-filter/', //TODO: DRUT! Wziąć docelowo ze zmiennej globalnej ustqawionej przez {% static... %}
                    dataType: 'json'
                },
                minimumInputLength: 2,
                language: "pl",
                width: '100%'
            });
        }

        if (mode === 'advanced') {
            $("#id_schedule-single_person_").select2({
                theme: 'bootstrap',
                ajax: {
                    method: 'post',
                    url: '/schedule/get-employees-for-meeting-filter/', //TODO: DRUT! Wziąć docelowo ze zmiennej globalnej ustqawionej przez {% static... %}
                    dataType: 'json'
                },
                minimumInputLength: 2,
                language: "pl",
                width: '100%'
            });
        }
    }

    function _setContent(mode) {
        if (mode === 'basic') {
            _setDefaultEventType();
        }
        scheduleForm.find("#id_schedule-start_date").val(startDate);
        scheduleForm.find("#id_schedule-end_date").val(endDate);
        scheduleForm.find('#id_schedule-title').val(title);
        scheduleForm.find('#id_schedule-type option[value="' + type + '"]').prop('selected', true);
        scheduleForm.find('#id_schedule-host_user option[value="' + hostUser + '"]').prop('selected', true);
        scheduleForm.find('#id_schedule-service option[value="' + service + '"]').prop('selected', true);
        scheduleForm.find('#headquarter_' + headquarter).fadeIn(200);
        scheduleForm.find('#id_schedule-headquarter option[value="' + headquarter + '"]').prop('selected', true);


        if (meetingRoom) {
            setMeetingRoom(meetingRoom);
        }
        getAvailableMeetingRooms(startDate, endDate);
    }

    _setTemplate();
    _setContent(mode);
}
