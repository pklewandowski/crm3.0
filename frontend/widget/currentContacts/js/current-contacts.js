import {SystemException} from "../../../_core/exception";

import "../scss/current-contacts.scss";
import {CurrentContactsRow} from "./current-contacts-row";
import {UserDetails} from "../../../user/userDetails/js/user-details";
import {HomeInfoPanel} from "../../../home/js/home-info-panel";



const className = 'CurrentContacts';

class CurrentContacts {
    constructor(container, dataUrls, title = '') {

        if (!container) {
            throw new SystemException(`[${className}]: Brak kontenetra dla widgetu`)
        }

        this.container = container;
        this.dataContainer = jsUtils.Utils.domElement('ul', null, 'widget-current-contacts-data-container');
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
            if (e.classList.contains('widget-current-contacts-row-container')) {
                this.details.render(e.dataset['id']);
            }
        });
    }

    _getData() {
        return ajaxCall(
            {
                method: 'get',
                url: this.dataUrls.currentContactsUrl,
                data: {p: this.page, mode: 'LIST'}
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
        if (!this.data) {
            return;
        }
        this.reset();

        if (!this.data.length) {
            this.dataContainer.appendChild(<div>Brak kontaktów</div>);
            return;
        }

        for (let row of this.data) {
            this.dataContainer.appendChild(CurrentContactsRow.render(row));
        }
    }

    render(page = 1, url) {
        this.page = page;
        this._getData().then((res) => {
            this.data = res.data;
            this._render(url);
        });
    }
}

export {CurrentContacts};