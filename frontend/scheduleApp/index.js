import {Calendar} from "../schedule/calendar/js/calendar";
import {CalendarType} from "../schedule/calendar/js/calendar-type";
import {SystemException} from "../_core/exception";

let calendar;

window.onload = () => {
    $("#datepicker11").datetimepicker({
        locale: "pl",
        inline: true,
        format: 'YYYY-MM-DD'
    });

    CalendarType.render(document.getElementById('calendarTypesContainer'));

    calendar = new Calendar(
        document.getElementById('calendarContainer'),
        false,
        null,
        null,
        {
            invited_users: [
                {id: _g.credentials.user.id, first_name: _g.credentials.user.first_name, last_name: _g.credentials.user.last_name}
            ],
            allowAllDayEvents: false,
            calendar: {
                slotDuration: '00:30:00',
                shortenedViewNames: true
            }
        }
    );

    calendar.setCalendar();

    $("#datepicker11").on('dp.change', (e) => {
        calendar.fullCalendar.gotoDate(e.date.format('YYYY-MM-DD'));
    });

};