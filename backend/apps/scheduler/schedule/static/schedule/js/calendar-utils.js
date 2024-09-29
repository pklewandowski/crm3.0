function refetchEvents() {
    $("#calendar").fullCalendar('refetchEvents');
    // $("#calendar").fullCalendar('rerenderEvents');
}

function toggleCalendarMode() {
    if (calendar_mode == 'event') {
        calendar_mode = 'room';
        $(".fc-eventRoomToggle-button").text('Widok zdarzeń');
    } else {
        calendar_mode = 'event';
        $(".fc-eventRoomToggle-button").text('Widok sal');
    }

    refetchEvents();
}

function toggleCalendarWindow() {
    let maximize = $('#calendar-container').hasClass('col-lg-12');
    if (maximize) {
        $('#calendar-side-view').show();
        $('#calendar-container').switchClass('col-lg-12', 'col-lg-10', 0);

    } else {
        $('#calendar-side-view').hide();
        $('#calendar-container').switchClass('col-lg-10', 'col-lg-12', 0);
    }
    //window.dispatchEvent(new Event('resize'));
    let width = $('#calendar .fc-view-container').width();
    //var width = Math.max($("#calendar .fc-view").width(), $('#calendar .fc-view-container').width());

    $("#calendar .fc-view").width(width);

    calendarWidth = width;
}


function setTimeRangeSlider(hourStart, hourEnd) {
    let slider = document.getElementById("timerange_slider"),
        leftValue = document.getElementById('leftvalue'),
        rightValue = document.getElementById('rightvalue');

// 0 = initial minutes from start of day
// 1439 = maximum minutes in a day
// step: 30 = amount of minutes to step by.
    let initialStartMinute = 540, //0
        initialEndMinute = 1080, //  1440,
        step = 15,
        margin = 15;

    if (slider.noUiSlider) {
        slider.noUiSlider.destroy();
    }
    slider = noUiSlider.create(slider, {
        // start: [initialStartMinute, initialEndMinute],
        connect: true,
        step: step,
        margin: margin,
        start: [hourStart, hourEnd],
        pips: {
            mode: 'values',
            values: [0, 360, 720, 1080, 1440],
            density: 4
        },

        range: {
            'min': initialStartMinute,
            'max': initialEndMinute
        }
    });

    let convertValuesToTime = function (values, handle) {

        values = values
            .map(value => Number(value) % 1441)
            .map(value => convertMinutesToHoursAndMinutes(value));
        return values;
    };

    let convertMinutesToHoursAndMinutes = function (minutes) {
        let hour = Math.floor(minutes / 60);
        let minute = minutes - hour * 60;
        return ("0" + hour).slice(-2) + ':' + ("0" + minute).slice(-2);

    };

    slider.on('update', function (values, handle) {
        t = convertValuesToTime(values, handle);
        if (t) {
            $('form#schedule-form').find('#start_hour').text(t[0]);
            $('form#schedule-form').find('#end_hour').text(t[1]);
        }
        // convertValuesToTime(values, handle);
    });

    $('.noUi-value.noUi-value-horizontal.noUi-value-large').each(function () {
        let val = $(this).html();
        val = recountVal(parseInt(val));
        $(this).html(val);
    });

    function recountVal(val) {
        switch (val) {
            case 0:
                return '00:00';
            case 120:
                return '02:00';
            case 240:
                return '04:00';
            case 360:
                return '6:00';
            case 720:
                return '12:00';
            case 1080:
                return '18:00';
            case 1440:
                return '24:00';
            default:
                return '00:00';
        }
    }
}


function resetCalendarMode() {
    calendar_mode = 'event';
}


function fillUserDataLink(data, className) {
    return '<a ' +
        'data-pk="' + data.pk + '" ' +
        'data-first_name="' + data.first_name + '" ' +
        'data-last_name="' + data.last_name + '" ' +
        'data-email="' + data.email + '" ' +
        'data-phone_one="' + data.phone_one + '" ' +
        'data-phone_two="' + data.phone_two + '" ' +
        'class="' + className + '" style="color:white">'
        + (data.first_name && data.first_name.length ? data.first_name[0] + '. ' : '') + data.last_name + '</a></div>';
}

function sortEventByCustomParam(prevEventObj, nextEventObj) {

    if (prevEventObj.id < nextEventObj.id) {
        return -1;
    } else {
        return 1;
    }
}

function zoomCalendar(dir) {

    let v = $('#calendar').find('.fc-view');
    switch (dir) {
        case '+':
            v.width(v.width() + 200);
            break;
        case '-':
            v.width(Math.max(v.width() - 200, $('#calendar .fc-view-container').width()));
            break;
        default:
            v.width($('#calendar .fc-view-container').width());
    }
    calendarWidth = v.width();
}


function vZoomCalendar(dir) {
    let s = $('#calendar').fullCalendar('option', 'slotDuration').split(':');

    let h = parseInt(s[0]) * 60;
    let m = parseInt(s[1]) + h;

    switch (dir) {
        case '-':
            m = Math.min(2 * m, 60);
            break;
        case '+':
            m = Math.max(m / 2, 15);
            break;

        default:
            m = 15;
            break;
    }

    let hr = pad(Math.floor(m / 60), 2);
    let mi = pad(m % 60, 2);

    $('#calendar').fullCalendar('option', 'slotDuration', `${hr}:${mi}:00`);
}


function setProductRetail() {
    "use strict";
    let productRetailList = $('#product_retail_container').find('table.product-retail-list tbody tr');
    if (productRetailList) {
        let cnt = parseInt($('#id_product_retail_client_formset-INITIAL_FORMS').val());
        productRetailList.each(function (i, e) {
            $.each($(e).find('input'), function (_i, _e) {
                let id = $(_e).prop('id');
                let name = $(_e).prop('name');
                $(_e).prop('id', id.replace(/__prefix__/g, cnt));
                $(_e).prop('name', name.replace(/__prefix__/g, cnt));
            });
            cnt++;
        });
        $('#id_product_retail_client_formset-TOTAL_FORMS').val(cnt);
    }
}

function setMeetingRoom(id) {

    $.each($('form#schedule-form input[name="schedule-meeting_room"]'), function (i, e) {
        if ($(this).val() == id) {
            $(this).prop("checked", true);
            $(this).closest('label').addClass('active');
            $("#defined_location_title").text($(this).data('name')).data('id', $(this).data('name'));
            // $("#defined_location_title").data('id', $(this).data('name'));
            return false;
        }
    });
}

function setEventPopover(element, event) {

    $('.popover').popover('hide');
    $(".tooltip").tooltip("hide");

    let address = event.data.custom_address ? event.data.custom_address : event.data.address;
    let eventTmpl = $('#event_popover_data_template').html();
    let participantList = '';

    $.each(event.data.invited_users, function (i, e) {
        let participantListTmpl = $('#event_popover_participant_data_template').html();
        participantListTmpl = participantListTmpl.replace("__NAME__", e.first_name + ' ' + e.last_name);
        participantListTmpl = participantListTmpl.replace("__PHONE__", e.phone_one);
        participantListTmpl = participantListTmpl.replace(/__USER_EDIT_LINK__/g, e._edit_link);
        participantListTmpl = participantListTmpl.replace("__EMAIL__", e.email);
        participantListTmpl = participantListTmpl.replace("__CONFIRMED__", e.confirmed ? 'check' : 'times');
        participantList += participantListTmpl;
    });

    //TODO: zamienić na ładowany template
    let participantListTable =
        "<table class=\"table table-hover table-condensed\">\n" +
        "        <thead>\n" +
        "        <tr>\n" +
        "            <th>Imię i nazwisko</th>\n" +
        "            <th>Tel</th>\n" +
        "            <th>E-mail</th>\n" +
        "            <th>Potwierdził</th>\n" +
        "        </tr>\n" +
        "        </thead>\n" +
        "        <tbody>\n" +
        "        __PARTICIPANT_LIST__\n" +
        "        </tbody>\n" +
        "    </table>";

    participantListTable = participantListTable.replace('__PARTICIPANT_LIST__', participantList);

    eventTmpl = eventTmpl.replace('__EVENT_ADDRESS__', address);
    eventTmpl = eventTmpl.replace('__PARTICIPANT_LIST_TABLE__', participantListTable);


    element.popover({container: 'body', placement: 'auto', trigger: "focus", title: event.title, html: true, content: eventTmpl});
    element.popover('show');
}

