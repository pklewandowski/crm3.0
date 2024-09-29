import "../scss/incoming-events.scss";

import {HomeInfoPanel} from "../../../home/js/home-info-panel";
import {incomingEventsRow} from "./incoming-events-row";
import {UserDetails} from "../../../user/userDetails/js/user-details";


const className = 'CurrentContacts';

class IncomingEvents {
    constructor(container, dataUrls, title = '') {
        this.container = jsUtils.Utils.setContainer(container, this.constructor.name);
        this.dataContainer = <ul className='widget-incoming-events-data-container'></ul>;
        this.dataUrls = dataUrls;
        this.page = null;
        this.data = null;

        this.infoPanel = new HomeInfoPanel(title);
        this.infoPanel.panelBody.classList.add('scroll-on-hover');
        this.infoPanel.panelBody.appendChild(this.dataContainer);

        this.container.appendChild(this.infoPanel.panel);

        this.details = new UserDetails(this.dataUrls.currentContactsUrl);

        this.dataContainer.addEventListener('click', (evt) => {
            let e = evt.target;
            if (e.classList.contains('widget-incoming-events-userList')) {
                this.details.render(e.dataset['id']);
            }
        });

        document.addEventListener('scheduleEvt:refetchEvents', ()=>{
            this.render();
        })
    }

    _getData() {
        return ajaxCall(
            {
                method: 'get',
                url: this.dataUrls.incomingEventsUrl,
                data: {user: _g.credentials.user.id, p: this.page, mode: 'LIST'}
            },
            null,

            (resp) => {
                jsUtils.LogUtils.log(resp.responseJSON.errmsg);
            }
        )
    }

    reset() {
        this.dataContainer.innerHTML = null;
    }

    _render() {
        if (!this.data?.length) {
            this.dataContainer.appendChild(<div>Brak nadchodzących wydarzeń</div>);
            return;
        }

        this.reset();

        for (let row of this.data) {
            this.dataContainer.appendChild(
                incomingEventsRow(
                    row.start_date,
                    row.end_date,
                    row.title,
                    row.type,
                    row.invited_users
                )
            );
        }
    }

    render(page = 1) {
        this.page = page;
        this._getData().then((res) => {
            this.data = res;
            this._render();
        });
    }
}

export {IncomingEvents};