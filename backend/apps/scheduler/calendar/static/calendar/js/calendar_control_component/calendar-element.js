let CalendarEntryTooltip = function (event) {
    "use strict";
    this.event = event;

    let _tooltipHeader = `<div><strong>${event.title}</strong> ${moment(this.event.start).format("HH:mm")}-${moment(this.event.end).format("HH:mm")} </div>`;

    let _setTooltipCustomLocation = function (event) {
        if (event.data.address.length) {
            return `<div><span>Lokalizacja: </span>${event.data.address}</div>`;
        }
    };

    let _setTooltipInvitedUsers = function (event) {
        if (event.data.invited_users.length) {
            let html = "<div>Uczestnicy:</div>";
            $.each(event.data.invited_users, function (i, item) {
                html += `<div>${item.first_name} ${item.last_name}</div>`;
            });
            return html;
        }
    };

    this.getTooltip = function () {
        let tooltip = _tooltipHeader;
        tooltip += _setTooltipCustomLocation(this.event);
        tooltip += _setTooltipInvitedUsers(this.event);
        return tooltip;
    }
};

let CalendarEntry = function (event, element) {
    "use strict";
    this.event = event;
    this.element = element;

    this.setTooltip = function () {
        if(this.element) {
            let tooltip = new CalendarEntryTooltip(event);
            $(this.element).tooltip({title: tooltip.getTooltip(), html: true, placement: 'auto', container: 'body'});
        }
    }
};