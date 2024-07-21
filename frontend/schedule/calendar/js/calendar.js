import {SystemException} from "../../../_core/exception";
import {Calendar as FullCalendar} from "@fullcalendar/core";
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import listPlugin from '@fullcalendar/list';
import interactionPlugin from '@fullcalendar/interaction';
import plLocale from '@fullcalendar/core/locales/pl'
import bootstrapPlugin from '@fullcalendar/bootstrap';
import {calendarModal} from "./calendar-modal";

import {CalendarEvent} from "../../js/calendar-event";
import {CalendarEventForm} from "../../form/js/calendar-event-form";

import "../scss/calendar.scss";
import {CalendarType} from "./calendar-type";

const className = 'Calendar';


class Calendar {
    constructor(container, isModal = false, calendarTypeId = null, calendarTriggerBtn = null, opts = {}) {
        this.promiseList = [];
        this.modal = null;
        this.calendarType = new CalendarType(calendarTypeId);
        this.calendarTriggerBtn = calendarTriggerBtn;
        this.event = new CalendarEvent();
        this.eventForm = new CalendarEventForm(this.calendarType);
        this.allowAllDayEvents = opts?.allowAllDayEvents;

        // Predefined participants list for an event.
        // If provided, the participants list will be prefilled with the data {id, FirstName, lastName}
        //todo: change invited_users to participants when deploy new (this) version of calendar in entire project
        this.invited_users = opts?.invited_users;

        if (opts.calendar.shortenedViewNames === true) {
            plLocale.buttonText.month = 'Mc.';
            plLocale.buttonText.week = 'Tydz.';
            plLocale.buttonText.day = 'Dz.';
            plLocale.buttonText.list = 'Pl. dn.';
        }

        this.defaultOpts = {
            plugins: [dayGridPlugin, timeGridPlugin, listPlugin, interactionPlugin, bootstrapPlugin],
            locale: plLocale,
            timeZone: 'local',
            // themeSystem: 'bootstrap',
            height: '100%',
            // dayHeaderFormat:{ weekday: 'short', month: 'numeric', day: 'numeric', omitCommas: true },
            dayHeaderFormat: {month: 'numeric', day: 'numeric', omitCommas: true}, // weekday not displayed
            initialView: 'businessWeek',
            selectable: true,
            editable: true,
            nowIndicator: true,
            slotEventOverlap: false,
            allDaySlot: false,
            slotDuration: '00:15:00',
            snapDuration: '00:15:00',
            displayEventTime: false, // todo: set it as an parameter option
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                // right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
                right: 'dayGridMonth,businessWeek,timeGridWeek,timeGridDay,listMonth'
            },
            views: {
                businessWeek: {
                    type: 'timeGridWeek',
                    duration: {
                        days: 7
                    },
                    buttonText: 'Tydz. rob.',
                    //minTime: '09:00:00',
                    //maxTime: '17:00:00',
                    title: '',
                    // scrollTime: gWorkingHours.start,
                    columnFormat: 'ddd DD.MM',
                    hiddenDays: [0, 6] // Hide Sunday and Saturday?
                }
            },
            select: info => {
                if (!this.allowAllDayEvents) {
                    if (
                        info.start.getFullYear() !== info.end.getFullYear() ||
                        info.start.getMonth() !== info.end.getMonth() ||
                        info.start.getDate() !== info.end.getDate()
                    ) {
                        Alert.warning('Wydarzenia wielodniowe nie są dozwolone w tym widoku.', '', () => {
                            this.fullCalendar.unselect();
                        });

                        return;
                    }
                }
                this.eventForm.show();
                this.eventForm.setData(
                    null,
                    info.startStr,
                    info.endStr,
                    _g.credentials.user.id,
                    {
                        title: '',
                        invited_users: this.invited_users
                    }
                );
            },
            eventClick: info => {
                this.event.getEvent(info).then(
                    event => {
                        this.eventForm.show();
                        this.eventForm.setData(event.id, event.start, event.end, event.host_user, event);
                    },
                    error => {
                        jsUtils.LogUtils.log(error);
                        Alert.error('Błąd', error);
                    }
                )
            },

            eventResize: info => {
                CalendarEvent.changeEventTime(info, 'resize');
            },

            eventDrop: info => {
                CalendarEvent.changeEventTime(info, 'move');
            },

            events: (info, successCallback, failureCallback) => {
                $(".tooltip").tooltip("hide");
                this.event.getEvents(info.startStr, info.endStr, successCallback, failureCallback, true);
            },
        };

        this.calendarOpts = Object.assign({}, this.defaultOpts, opts?.calendar);

        if (isModal) {
            this.modal = document.getElementById('calendarModal');

            if (!this.modal) {
                this.modal = <div className="calendarModal modal fade"></div>;
                this.modal.role = "dialog";
                this.modal.appendChild(calendarModal);

                document.body.appendChild(this.modal);
            }

            this.container = this.modal.querySelector('.calendar-body');

            if (calendarTriggerBtn) {
                this.calendarTriggerBtn.addEventListener('click', () => {
                    this.showCalendarModal();
                });
            }

            if (this.modal) {
                this.setCalendar();
                // this.render();
                let _this = this;

                $(this.modal).on('shown.bs.modal', function () {
                    // _this.setCalendar();
                    _this.render();
                });
                // $(this.modal).on('hide.bs.modal', function () {
                //     _this.fullCalendar.destroy();
                // });
            }

        } else {
            if (!container) {
                throw new SystemException(`[${className}]: No container provided`)
            }
            if (jsUtils.Utils.isDomElement(container)) {
                if (container.tagName === 'DIV') {
                    this.container = container;
                } else {
                    throw new SystemException(`[${className}]: container must be a div`);
                }

            } else {
                this.container = document.getElementById(container);
                if (!this.container || this.container.tagName !== 'DIV') {
                    throw new SystemException(`[${className}]: container must be a div`);
                }
            }
        }

        this.fullCalendar = null;

        document.addEventListener('scheduleEvt:refetchEvents', () => {
            if (this.fullCalendar) {
                this.fullCalendar.refetchEvents();
            }
        });

        this.init();
    }

    showCalendarModal() {
        $(this.modal).modal({backdrop: 'static', keyboard: false});
    }

    setCalendar(render = true) {
        Promise.all(this.promiseList).then(() => {
            this.fullCalendar = new FullCalendar(this.container, this.calendarOpts);
            if (render) {
                this.fullCalendar.render();
            }
            return this;
        });
    }

    render() {
        Promise.all(this.promiseList).then(() => {
            this.fullCalendar.render();
        });
    }

    _initConfig() {
        let _this = this;
        this.promiseList.push(
            this.calendarType.init().then(
                () => {
                    _this.eventForm.setEventTypes(_this.calendarType.allowed_event_types);
                },
                (err) => {
                    throw new SystemException(err)
                }
            )
        );
        // this.promiseList.push(
        //     new Promise((resolve, reject) => {
        //         this.calendarType.getEventTypes().then(() => {
        //             this.eventForm.setEventTypes(this.calendarType.events);
        //                 resolve();
        //             },
        //             () => {
        //                 reject()
        //             }
        //         );
        //     })
        // );

        // return new Promise((resolve, reject) => {
        //     this.event.getEventTypes().then(() => {
        //             this.eventForm.setEventTypes(this.event.types);
        //             resolve();
        //         },
        //         () => {
        //             reject();
        //         }
        //     )
        // })
    }

    init() {
        this._initConfig();
        // this.promiseList.push(pr);

        //pr.then(() => {
        // if (this.modal) {
        //     $(this.modal).on('shown.bs.modal', function () {
        //         _this.setCalendar();
        //         _this.render();
        //     });
        //     $(this.modal).on('hide.bs.modal', function () {
        //         _this.fullCalendar.destroy();
        //     });
        // }
        //});
    }
}

export {Calendar};