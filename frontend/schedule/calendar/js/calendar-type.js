import {SystemException} from "../../../_core/exception";

class CalendarType {
    constructor(calendarTypeId) {
        // if (!calendarTypeId) {
        //     throw new SystemException(`${CalendarType.constructor.name}: no calendar type ID specified`);
        // }
        this.calendarTypeId = calendarTypeId;
        this.name = null;
        this.allowed_view_types = null;
        this.allowed_event_types = null;
        this.is_default = null;

    }

    static getTypes() {
        return new Promise((resolve, reject) => {
            ajaxCall({
                method: 'get',
                url: '/schedule/api/calendar-type/',
                data: {id: '__all__'}
            }).then(
                data => {
                    resolve(data);
                },
                error => {
                    reject(error);
                    throw new SystemException(error);
                }
            );
        });
    }


    static render(container) {
        CalendarType.getTypes().then((ct) => {
                let ul = <ul></ul>;
                for (let i of ct) {
                    let li = <li id={i.id}><input type="checkbox"/>{i.name}</li>;
                    ul.appendChild(li);
                }
                container.appendChild(ul);
            }
        )
    }

    _set() {
        return ajaxCall({
            method: 'get',
            url: '/schedule/api/calendar-type/',
            data: {id: this.calendarTypeId}
        }).then(
            data => {
                this._mapData(data);
            },
            error => {
                throw new SystemException(error);
            })
    }

    _mapData(data) {
        this.calendarTypeId = data.id;
        this.name = data.name;
        this.allowed_view_types = data.allowed_view_types;
        this.allowed_event_types = data.allowed_event_types;
    }

    init() {
        return this._set();
    }
}

export {
    CalendarType
}
