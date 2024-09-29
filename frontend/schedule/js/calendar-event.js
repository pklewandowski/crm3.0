import {DateUtils} from "../../_core/utils/date-utils";

class CalendarEvent {
    constructor() {
        this.types = null;
    }

    /**
     * getEvents - retrieve event list for
     * @param startDate
     * @param endDate
     * @param successCallback
     * @param failureCallback
     * @param onlyUser - flag if get events only where the logged user is participant
     */
    getEvents(startDate, endDate, successCallback, failureCallback, onlyUser = false) {
        ajaxCall({
            url: '/schedule/api/events/',
            method: 'get',
            data: {startDate: startDate, endDate: endDate, user: onlyUser ? _g.credentials.user.id : null}
        }).then(
            (data) => {
                let mappedData = this._mapData(data);
                successCallback(mappedData);
            },
            (err) => {
                failureCallback(err);
            }
        );
    }

    getEvent(eventInfo) {
        return new Promise((resolve, reject) => ajaxCall({
                method: 'get',
                url: '/schedule/api/events/',
                data: {id: eventInfo.event.id}
            }).then(
                data => {
                    resolve(this._mapData([data])[0]);
                },
                error => {
                    reject(error);
                })
        )
    }

    async getEventTypes() {
        if (!this.types) {
            await ajaxCall(
                {
                    method: 'get',
                    url: '/schedule/api/types/'
                },
                (types) => {
                    this.types = types;
                    return this.types;
                },
                (error) => {
                    jsUtils.LogUtils.log(error);
                    Alert.error('Błąd', error);
                }
            )
        } else {
            return this.types;
        }
    }

    _mapData(data) {
        if(!data || !Array.isArray(data)) {
            return [];
        }
        return data.map(x => {
            return Object.assign({}, x, {
                id: x.id ? x.id : null,
                start: new Date(x.start_date),
                end: new Date(x.end_date),
                // title: x.title,
                color: x.type.color
            })
        });
    }

    static saveEvent(data) {
        return new Promise((resolve, reject) => {
            ajaxCall({
                url: '/schedule/api/events/',
                method: data.id ? 'put' : 'post',
                data: {formData: JSON.stringify(data)}
            }).then(
                data => {
                    resolve(data);
                },
                error => {
                    reject(error);
                }
            )
        });
    }

    static deleteEvent(idEvent) {
        return new Promise((resolve, reject) => {
            ajaxCall({
                url: '/schedule/api/events/',
                method: 'delete',
                data: {idEvent: idEvent}
            }).then(
                data => {
                    resolve(data);
                },
                error => {
                    reject(error);
                }
            )
        });
    }

    static changeEventTime(info, type) {
        let txt;
        switch (type) {
            case 'resize':
                txt = 'czas trwania';
                break;
            case 'move':
                txt = 'czas';
                break;
            default:
                break;
        }
        Alert.questionWarning(`Czy na pewno zmienić ${txt} wydarzenia?`, '', () => {
                ajaxCall({
                    method: 'put',
                    url: '/schedule/api/events/',
                    data: {
                        action: 'CHANGE_TIME',
                        id: info.event.id,
                        start: DateUtils.formatDate(info.event.start, true, true),
                        end: DateUtils.formatDate(info.event.end, true, true),
                    }
                }).then(
                    () => {
                        document.dispatchEvent(new Event('scheduleEvt:refetchEvents'));
                    },
                    (error) => {
                        info.revert();
                        Alert.error('Błąd!', error);
                    }
                )
            },
            null,
            () => {
                info.revert();
            }
        );
    }
}

export {CalendarEvent};