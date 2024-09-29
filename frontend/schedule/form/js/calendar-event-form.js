import {calendarEventFormModal} from "./calendar-event-form-modal";
import {CalendarEvent} from "../../js/calendar-event";

import "../scss/calendar-event-form.scss";
import {DateUtils} from "../../../_core/utils/date-utils";
import {GoogleMapControl} from "../../../_core/controls/map-control/js/google-map-control";
import {SystemException} from "../../../_core/exception";

import {setSelect2} from "../../../_core/autocomplete";
import {ToolbarUtils} from "../../../_core/utils/toolbar-utils";

const className = 'CalendarEventForm';

class CalendarEventForm {
    constructor() {
        this.eventTypes = [];
        this.id = null;
        this.start = null;
        this.end = null;
        this.title = null;
        this.description = null;

        this.reminders = [];
        this.participants = [];

        this.modal = jsUtils.Utils.domElement('div', null, ['calendar-event-form-modal', 'modal', 'fade']);
        this.modal.role = "dialog";
        this.modal.innerHTML = calendarEventFormModal;

        document.body.appendChild(this.modal);

        this.addParticipantControl = this.modal.querySelector('.eventAddParticipant select');
        this.addParticipantControl.dataset['autocomplete_url'] = "/user/api/get-for-select2/";
        setSelect2($(this.addParticipantControl), true, null, {allowClear: false});

        this.eventTypeControl = this.modal.querySelector('.eventType');
        this.eventDeleteBtn = this.modal.querySelector('.deleteEventBtn');

        $(this.addParticipantControl).on('select2:select', () => {
            let data = $(this.addParticipantControl).select2('data')[0];
            $(this.addParticipantControl).val(null).trigger('change');
            this.addParticipant({id: data.id, firstName: data.firstName, lastName: data.lastName});
        });

        this.modalBody = this.modal.querySelector('.calendar-event-form-body');
        if (!this.modalBody) {
            throw new SystemException(`[${className}]: couldn't find form modal body`);
        }
        this.modal.querySelector(`.saveEventBtn`).addEventListener('click', () => {
            this.save();
        });

        this.modal.querySelector(`.deleteEventBtn`).addEventListener('click', () => {
            this.delete(this.id);
        });

        this.location = new GoogleMapControl(this.modalBody.querySelector('.eventLocation'), null, false);
        $(this.modal).on('shown.bs.modal', () => {
            this.location.render();
        });

        // for (let i of Array.from(this.modalBody.querySelectorAll('.datetime-field'))) {
        //     new Datepicker(i, {
        //         autohide: true,
        //         showOnClick: true,
        //         language: 'pl',
        //         format: 'yyyy-mm-dd'
        //     });
        //
    }

    reset() {
        for (let i of (Array.from(
            this.modalBody.querySelectorAll('input, select, textarea')
        ))) {
            i.value = null;
            i.checked = false;
        }
        Input.setValue(Input.getByName('eventAddressCountry'), 'Polska');
        this.modalBody.querySelector('.eventParticipants ul').innerHTML = null;
        this.eventTypeControl.value = this.eventTypeControl.options[0].value;
        this.eventTypeControl.options[0].selected = true;
        this.location.reset();
    }

    setData(id, start, end, user, opts = null) {
        this.id = id;
        this.start = new Date(start);
        this.end = new Date(end);
        this.title = opts ? opts.title : '';
        this.eventType = opts?.type?.id ? opts.type.id : null;
        this.description = opts?.description ? opts.description : '';
        this.participants = opts?.invited_users ? opts.invited_users.map(x => {
            return {id: x.id, lastName: x.last_name, firstName: x.first_name}
        }) : [];

        this.location.setAddress(opts.custom_location_address);
        this.eventIsPrivate = opts?.is_private;

        this.renderData();
    }

    setEventTypes(types) {
        if (!types) {
            return;
        }
        if (this.eventTypes.length) {
            return;
        }

        if (!Array.isArray(types)) {
            throw new SystemException(`[${className}]::setEventTypes: event type list must be of Array type)`);
        }

        this.eventTypes = types;

        for (let i in this.eventTypes) {
            let opt = new Option(this.eventTypes[i].name, this.eventTypes[i].id, false, i == 0);
            this.eventTypeControl.appendChild(opt);
        }
    }

    renderData() {
        // todo: separate _renderData function
        this.modalBody.querySelector('.eventStart').value = DateUtils.formatDate(this.start, true);
        this.modalBody.querySelector('.eventEnd').value = DateUtils.formatDate(this.end, true);
        this.modalBody.querySelector('.eventTitle').value = this.title;
        this.modalBody.querySelector('.eventDescription').value = this.description;
        this.modalBody.querySelector('.eventType').value = this.eventType;
        this.modalBody.querySelector('.eventIsPrivate').checked = this.eventIsPrivate;

        // if(location) {
        //     setMapLocation();
        // }

        for (let participant of this.participants) {
            this.addParticipant(participant);
        }

        if (this.id) {
            this.eventDeleteBtn.style.display = 'inline-block';
        } else {
            this.eventDeleteBtn.style.display = 'none';
        }
    }

    _getParticipants() {
        return Array.from(this.modal.querySelectorAll('.eventParticipants ul li')).map(x => x.value);
    }

    _getParticipantItem(participant) {
        let li = jsUtils.Utils.domElement(
            'li',
            null,
            'schedule-form-participants-item',
            null,
            participant.id.toString(),
            null);
        li.dataset['id'] = participant.id;
        li.dataset['participant'] = participant;

        li.appendChild(jsUtils.Utils.domElement(
            'div',
            null,
            'participant-item-name',
            null,
            null,
            null,
            `${participant.firstName} ${participant.lastName}`));

        let delBtn = ToolbarUtils.deleteBtn(null, true);
        delBtn.classList.add('event-participant-delete-btn');
        delBtn.addEventListener('click', (e) => {
            let target = e.target.closest('li');
            Alert.questionWarning('Czy na pewno usunąć uczestnika?', '', () => {
                target.remove();
            });
        });
        li.appendChild(delBtn);

        return li;
    }

    addParticipant(participant) {
        this.modalBody.querySelector('.eventParticipants ul').appendChild(this._getParticipantItem(participant));
    }

    getData() {
        return {
            id: this.id ? this.id : null,
            start: DateUtils.formatDate(this.start, true, true),
            end: DateUtils.formatDate(this.end, true, true),
            title: Input.getValue(this.modal.querySelector('.eventTitle')),
            type: Input.getValue(this.modal.querySelector('.eventType')),
            description: Input.getValue(this.modal.querySelector('.eventDescription')),
            participants: this._getParticipants(),
            location: this.location.getAddress(),
            is_private: this.modal.querySelector('.eventIsPrivate').checked
        }
    }

    show(reset = true) {
        if (reset) {
            this.reset();
        }
        $(this.modal).modal({backdrop: 'static', keyboard: false});
    }

    save(ask = false) {
        let _this = this;

        function _save() {
            CalendarEvent.saveEvent(_this.getData()).then(
                () => {
                    $(_this.modal).modal('hide');
                    document.dispatchEvent(new Event('scheduleEvt:refetchEvents'));
                },
                (err) => {
                    Alert.error('Błąd!', err.responseJSON.errmsg);
                }
            );
        }

        let title, txt;
        if (this.id) {
            title = 'Aktualizacja wydarzenia';
            txt = 'Czy na pewno zmienić dane wydarzenia?';
        } else {
            title = 'Nowe wydarzenie';
            txt = 'Czy na pewno dodać nowe wydarzenie?';
        }

        if (ask) {
            Alert.questionWarning(
                title,
                txt,
                () => {
                    _save();
                })
        } else {
            _save();
        }
    }

    delete(idEvent) {
        let _this = this;

        function _delete() {
            CalendarEvent.deleteEvent(idEvent).then(
                () => {
                    $(_this.modal).modal('hide');
                    document.dispatchEvent(new Event('scheduleEvt:refetchEvents'));
                },
                (err) => {
                    Alert.error('Błąd!', err.responseJSON.errmsg);
                }
            );
        }

        Alert.questionWarning(
            'Czy na pewno usunąć wydarzenie?',
            '',
            () => {
                _delete();
            });
    }
}

export {CalendarEventForm}