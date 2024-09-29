/**
 * Calendar control definition
 */

let calendarWidth;
let calendarMode = 'events';
let availableDates = [];
let drag = false;
let calendarInitialWidth;

// let hdqControlText = '<input type="checkbox" value="__HEADQUARTER_VALUE__"/><p>__HEADQUARTER_LABEL__</p>';
let hdqControlText = '<option value="__HEADQUARTER_VALUE__">__HEADQUARTER_LABEL__</option>';

function setMultipleHeadquarters() {
    if (gUserHeadquarters.length > 1) {
        $(".fc-left").append(
            '<div class="btn-group" role="group">' +
            '<button class="dropdown-toggle btn btn-default" type="button"\n' +
            'data-toggle="dropdown" id="user_headquerters_btn" aria-haspopup="true"\n' +
            'aria-expanded="false">Oddział</button>\n' +
            '<div class="dropdown-menu" aria-labelledby="user_headquerters_btn">' +
            '<ul data-choosen="" id="user_headquerters_list">' +

            '</ul>' +
            '</div>' +
            '</div>');

        $.each(gUserHeadquarters, function (i, e) {
            $("#user_headquerters_list").append(
                hdqControlText.replace('__HEADQUARTER_VALUE__', e.id).replace('__HEADQUARTER_LABEL__', e.name)
            );
        });
    }
}

function setHeadquarters() {
    $(".fc-left").append(
        '<div class="btn-group" role="group">' +
        '<select id="user_headquarters_list" class="form-control input-sm">' +
        '<option value="" style="color: #969696;">wszystkie dostępne oddziały</option>' +
        '</select>' +
        '</div>'
    );

    $.each(gUserHeadquarters, function (i, e) {
        $("#user_headquarters_list").append(
            hdqControlText.replace('__HEADQUARTER_VALUE__', e.id).replace('__HEADQUARTER_LABEL__', e.name)
        );
    });
}

$(document).ready(function () {

    $('#calendar').fullCalendar({
        customButtons: {
            filter: {
                text: 'Filtruj',
                click: function () {
                    $("#scheduleFilterModal").modal('show');
                }
            },
            eventRoomToggle: {
                text: "Widok sal",
                click: function () {
                    toggleCalendarMode();
                }
            },
            fullScreen: {
                icon: 'fa-search',
                click: function () {
                    toggleCalendarWindow();
                }
            },

            // zoomIn: {
            //     icon: 'fa-arrow-right',
            //     click: function () {
            //         zoomCalendar('+');
            //     }
            // },
            // zoomOut: {
            //     icon: 'fa-arrow-left',
            //     click: function () {
            //         zoomCalendar('-');
            //     }
            // },
            // zoomDefault: {
            //     icon: '',
            //     click: function () {
            //         zoomCalendar();
            //     }
            // },
            //
            // vZoomIn: {
            //     icon: 'fa-arrow-left',
            //     click: function () {
            //         vZoomCalendar('+');
            //     }
            // },
            // vZoomOut: {
            //     icon: 'fa-arrow-left',
            //     click: function () {
            //         vZoomCalendar('-');
            //     }
            // },
            // vZoomDefault: {
            //     icon: '',
            //     click: function () {
            //         vZoomCalendar();
            //     }
            // }
        },

        buttonText: {
            today: 'Dziś',
            month: 'M-c',
            week: 'Tydz.',
            bussinessWeek: 'Tydz. rob.',
            day: 'Dz.',
            list: 'list'
        },
        header: {
            left: 'prev,next today, filter,eventRoomToggle',
            center: 'title',
            //right: 'month,agendaWeek,businessWeek,agendaDay,listWeek'
            // right: 'vZoomIn,vZoomDefault,vZoomOut, zoomOut,zoomDefault,zoomIn, month,agendaWeek,businessWeek,agendaDay, fullScreen'
            right: 'month,agendaWeek,businessWeek,agendaDay, fullScreen'
        },
        views: {
            businessWeek: {
                type: 'agendaWeek',
                duration: {
                    days: 7
                },
                buttonText: 'Tydz. rob.',
                //minTime: '09:00:00',
                //maxTime: '17:00:00',
                title: '',
                scrollTime: gWorkingHours.start,
                columnFormat: 'ddd DD.MM',
                hiddenDays: [0, 6] // Hide Sunday and Saturday?
            }
        },
        // eventOrder: 'id',
        //columnFormat: 'ddd DD.MM',
        themeSystem: 'bootstrap3',
        slotEventOverlap: false,
        slotDuration: '00:15:00',
        snapDuration: '00:15:00',
        allDaySlot: false,
        defaultView: 'agendaWeek',
        scrollTime: gWorkingHours.start,
        contentHeight: 600,
        //height: function() {return pixel height of calendar TODO: zrobić !!!},
        businessHours: {
            // days of week. an array of zero-based day of week integers (0=Sunday)
            dow: [1, 2, 3, 4, 5], // Monday - Thursday

            start: gWorkingHours.start, // a start time (10am in this example)
            end: gWorkingHours.end, // an end time (5pm in this example)
        },
        //height: 600,//height: 'auto',
        //aspectRatio: 1,
        //defaultView: 'agendaWeek',
        lang: 'pl',
        //defaultDate: '2016-06-12',
        selectable: true,
        selectHelper: true,
        editable: true,
        eventLimit: true, // allow "more" link when too many events
        displayEventTime: false,
        weekNumberCalculation: 'ISO',
        firstDay: '1',

        compareEventSegs: function (t, e) {
            return sortEventByCustomParam(t.event, e.event);
        },

        viewRender: function () {
            $('#calendar div.fc-slats table tbody tr').each(function () {

                if ($(this).data('time').substring(3) === '00:00') {
                    $(this).addClass('calendar-full-hour-tr');
                    $(this).find('td').addClass('calendar-full-hour-td');
                }
            });
            if (calendarWidth) {
                $('#calendar .fc-view').width(calendarWidth);
            }

            $(".fc-fullScreen-button").html('<i class="fa fa-arrows-alt"></i>');

            $(".fc-zoomIn-button").html('<i class="fa fa-arrow-right"></i>');
            $(".fc-zoomOut-button").html('<i class="fa fa-arrow-left"></i>');
            $(".fc-zoomDefault-button").html('<i class="fa fa-circle-o"></i>');

            $(".fc-vZoomIn-button").html('<i class="fa fa-arrow-down"></i>');
            $(".fc-vZoomOut-button").html('<i class="fa fa-arrow-up"></i>');
            $(".fc-vZoomDefault-button").html('<i class="fa fa-circle-o"></i>');
        },
        eventOrder: function () {
            return false;
        },

        select: function (start, end) {
            let mEnd = $.fullCalendar.moment(end);
            let mStart = $.fullCalendar.moment(start);
            let wholeDayOnly = false;

            let view = $('#calendar').fullCalendar('getView');

            if (view.name !== 'month') {
                if (mEnd.isAfter(mStart, 'day')) {
                    $('#calendar').fullCalendar('unselect');
                    swal('Rejestrowanie zdarzeń wielodniowych jest dozwolone jedynie w widoku miesiąca.', 'W obecnym widoku można tworzyć zdarzenia jedynie w obrębie jednego dnia', 'warning');
                    return;
                }
            } else {
                wholeDayOnly = true;
            }

            // resetEventForm('schedule-form', wholeDayOnly ? 'advanced': 'basic', wholeDayOnly);
            // setInitialData(start, end);
            // setEventFormAccess(true);
            //
            // getAvailableMeetingRooms(start.format('YYYY-MM-DD HH:mm'), end.format('YYYY-MM-DD HH:mm'));
            //
            // $("#schedule-form").find("#submit-btn").show();

            $('#addScheduleFormModal').modal('show');
            $("#formIframe").attr('src', gAddActionUrl)
        },

        events: function (start, end, timezone, callback) {
            $(".tooltip").tooltip("hide");
            $(".loader-container").fadeIn();
            getEvents(start, end, callback);
        },

        eventClick: function (calEvent, jsEvent, view) {

            let wholeDayOnly=false;

            $('.popover').popover('hide');
            if (!calEvent.viewable) {
                swal('Brak uprawnień do przeglądania szczegółów', '', 'warning');
                return;
            }
            if (!calEvent.details_viewable) {
                return;
            }

            if (calEvent.data.whole_day) {
                wholeDayOnly = true;
            }
            resetEventForm('schedule-form', 'advanced', wholeDayOnly);
            getEventData(calEvent, calendar_get_event_url);
        },

        eventResize: function (event, delta, revertFunc) {
            let mEnd = $.fullCalendar.moment(event.end);
            let mStart = $.fullCalendar.moment(event.start);

            let view = $('#calendar').fullCalendar('getView');

            // if (view.name !== 'month') {
                if (mEnd.isAfter(mStart, 'day')) {
                    $('#calendar').fullCalendar('unselect');
                    revertFunc();
                    swal('Rejestrowanie zdarzeń wielodniowych jest dozwolone jedynie w widoku miesiąca.', 'W obecnym widoku można tworzyć zdarzenia jedynie w obrębie jednego dnia', 'warning');
                    return;
                }
            // }
            moveEvent(calendar_move_event_url, event, revertFunc);
            event.data.confirmed = false;
        },

        eventDrop: function (event, delta, revertFunc) {
            let mEnd = $.fullCalendar.moment(event.end);
            let mStart = $.fullCalendar.moment(event.start);

                if (mEnd.isAfter(mStart, 'day')) {
                    $('#calendar').fullCalendar('unselect');
                    swal('Rejestrowanie zdarzeń wielodniowych jest dozwolone jedynie w widoku miesiąca.', 'W obecnym widoku można tworzyć zdarzenia jedynie w obrębie jednego dnia', 'warning');
                    revertFunc();
                    return false;
                }

            moveEvent(calendar_move_event_url, event, revertFunc);
            event.data.confirmed = false;
        },

        eventDragStart: function (event, jsEvent) {
            drag = true;
            $(".tooltip").tooltip("hide");
            $('.popover').popover('hide');
        },

        eventDragStop: function () {
            drag = false;
        },

        eventRender: function (event, element) {

            let cEvent = new CalendarEntry(event, element);

            $(".tooltip").tooltip("hide");
            $('.popover').popover('hide');

            if (event.id) {
                if (event.viewable) {

                    if (!drag && event.rendering !== 'background') {
                        cEvent.setTooltip();
                    }

                    element.find('.fc-content').append('<div style="display:inline-block">'
                        + (event.data.address ? event.data.address : '') + '</div>');

                    for (let i in event.data.invited_users) {
                        element.append('<div style="width:100%; overflow:hidden; display:inline-block;">'
                            + fillUserDataLink(event.data.invited_users[i], 'userdata-lnk') + '</div>');
                    }

                    element.contextmenu(function () {
                        return false;
                    });

                    element.mousedown(function (e) {
                        if (e.button === 2) {
                            setEventPopover($(this), event);
                            return false;
                        }
                        return true;
                    });

                    if (event.data && !event.data.confirmed) {
                        element.find('.fc-bg').addClass('event-not');
                    }
                    element.find('.fc-content').css('background', event.color);

                } else {
                    if (calendar_mode !== 'room') {
                        element.find('.fc-content').text('Zdarzenie');
                    }
                    element.css('background', '#AAAAAA');
                    element.find('.fc-content').css('background', '#777777');
                }

                if (event.data) {
                    if (!event.data.resizable) {
                        element.find('.fc-end-resizer').hide();
                    }

                    if (event.data.opacity) {
                        element.css('opacity', event.data.opacity)
                    }

                    if (event.data.status === 'AN' || event.data.status === 'CL') {
                        element.css('opacity', 0.6);
                        if (event.data.status === 'AN') {
                            element.find('.fc-title').css('text-decoration', 'line-through');
                        }

                        if (event.data.status === 'CL') {
                            element.find('.fc-title').css('font-style', 'italic');
                        }
                    }

                    if (event.editable) {
                        element.find('.fc-title').css('text-decoration', 'underline');
                        element.find('.fc-title').css('font-weight', 700);
                    }
                }
            }
        },

        eventAfterRender: function (event, element, view) {
        },

        eventAfterAllRender: function (view) {
            $('.loader-container').fadeOut();
        }
    });
    setHeadquarters();
    // $("#user_headquerters_list").find('input[type=checkbox]').click(function () {
    //     $("#calendar").fullCalendar('refetchEvents');
    // });
    $("#user_headquarters_list").change(function () {
        $("#calendar").fullCalendar('refetchEvents');
    })

});
