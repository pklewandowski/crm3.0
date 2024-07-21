class Schedule {
    /**
     * getEvents - retrieve evet list for
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
                let mappedData = data.map(x => {
                    return {
                        id:x.id,
                        start: new Date(x.start_date),
                        end: new Date(x.end_date),
                        title: x.title,
                        color: x.type.color
                    }
                });
                successCallback(mappedData);
            },
            (err) => {
                failureCallback(err);
            }
        );
    }

    static addEvent(data) {
        return new Promise((resolve, reject) => {
            ajaxCall({
                url: '/schedule/api/events/',
                method: 'post',
                data: {formData: JSON.stringify(data)}
            }).then(
                (data) => {
                    resolve(data);
                },
                (err) => {
                    reject(err);
                }
            )
        });
    }
}

export {Schedule};