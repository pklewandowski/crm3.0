import {SystemException} from "../../../_core/exception";
import {Format} from "../../../_core/format/format";
import {getPersonalTitle} from "../../js/utils";
import {modalTemplate} from "./modal-template";

import "../scss/user-details.scss";

import {Avatar} from "../../avatar/js/avatar";
import {Note} from "../../../note/js/note";

import {Calendar} from "../../../schedule/calendar/js/calendar";

const className = 'UserDetails';

class UserDetails {
    constructor(url) {
        if (!url) {
            throw new SystemException(`[${className}]: no data retireve url`)
        }

        this.calendarOpts = {
            invited_users: [],
            allowAllDayEvents: false,
            calendar: {
                slotDuration: '00:30:00',
                shortenedViewNames: true
            }
        };

        this.modal = document.getElementById('userDetailsModal');

        if (!this.modal) {
            this.modal = jsUtils.Utils.domElement('div', 'userDetailsModal', ['modal', 'fade']);
            this.modal.role = "dialog";
            this.modal.appendChild(modalTemplate);

            document.body.appendChild(this.modal);
        }

        this.container = this.modal.querySelector('.widget-user-details-container');

        if (!this.container) {
            throw new SystemException(`[${className}]: no container`)
        }

        this._getInnerContainers();

        this.url = url;
        this.data = null;


        $(this.modal).on('shown.bs.modal', () => {
            if (this.eventsContainer) {
                this.calendar = new Calendar(
                    this.eventsContainer,
                    false,
                    null,
                    null,
                    this.calendarOpts
                );
                this.calendar.setCalendar();
            }
        });
    }

    _getInnerContainers() {
        this.avatarContainer = this.modal.querySelector('.widget-user-details-avatar');
        this.titleContainer = this.modal.querySelector('.widget-user-details-title');
        this.personalDataContainer = this.modal.querySelector('.widget-user-details-personal-data');
        this.addressContainer = this.modal.querySelector('.widget-user-details-address');
        this.notesContainer = this.modal.querySelector('.widget-user-details-notes');
        this.eventsContainer = this.modal.querySelector('.widget-user-details-events');
        this.documentsContainer = this.modal.querySelector('.widget-user-details-documents-data');
        this.productsContainer = this.modal.querySelector('.widget-user-details-products');
    }

    getDetails(id) {
        return ajaxCall({
            method: 'get',
            url: this.url,
            data: {id: id, mode: 'DETAILS'}
        });
    }

    reset() {
        if (this.avatarContainer) {
            this.avatarContainer.innerHTML = null;
        }
        this.titleContainer.innerHTML = null;
        this.personalDataContainer.innerHTML = null;
        this.notesContainer.innerHTML = null;
        if (this.eventsContainer) {
            this.eventsContainer.innerHTML = null;
        }
        if (this.documentsContainer) {
            this.documentsContainer.innerHTML = null;
        }
        if (this.productsContainer) {
            this.productsContainer.innerHTML = null;
        }
    }

    _renderAvatar() {
        if (!this.avatarContainer) {
            return;
        }
        this.avatarContainer.appendChild(
            new Avatar(
                this.data.user.avatar_filename,
                {firstName: this.data.user.first_name, lastName: this.data.user.last_name}).render()
        );
    }

    _renderHeaderData() {
        this.titleContainer.innerHTML = `<a href="/user/edit/${this.data.user.id}/CLIENT/">${getPersonalTitle(this.data.user)}</a>`;
        this._renderPersonalData();
    }

    _renderHeader() {
        this._renderAvatar();
        this._renderHeaderData();
    }

    _renderTags() {
        let html = '';
        if (!this.data?.user?.tags?.length) {
            return "<span>-</span>";
        }

        for (let i of this.data.user.tags) {
            html += `<span class="widget-user-details-personal-data-tags">${i}</span>`;
        }
        return html;
    }

    _renderNotes(id) {
        let notes = new Note(id, '/user/api/note/', document.querySelector('.note-container'));
        notes.setNotes(this.data.notes).render();
    }

    _renderEvents() {
        for (let i of this.data.events) {
            let table = jsUtils.Utils.domElement('table', '', ['table', 'table-hover']);
            let thead = jsUtils.Utils.domElement('thead', '', 'table');
            let tbody = jsUtils.Utils.domElement('tbody');

            thead.innerHTML = `<tr><td></td></tr>`;

            table.appendChild(thead);
            table.appendChild(tbody);
        }
    }

    _renderDocuments() {
        if (!this.documentsContainer) {
            return;
        }
        let container = <div></div>;

        this.documentsContainer.appendChild(container);

        if (!this.data.documents.length) {
            this.documentsContainer.innerText = 'brak produktów';
            return;
        }

        let table = jsUtils.Utils.domElement('table', '', 'table');
        let thead = jsUtils.Utils.domElement('thead', '', 'table');
        let tbody = jsUtils.Utils.domElement('tbody');

        thead.innerHTML = `
                <tr>
                    <th>Nr wniosku</th>
                    <th>data utworzenia</th>                    
                    <th>Status</th>
                    <th>Data startu pożyczki</th>
                    <th>Wartość</th>
                    <th>Kapitał netto</th>          
                </tr>
            `;

        tbody.innerHTML = '';

        for (let i of this.data.documents) {
            tbody.innerHTML += `
            <tr>
                <td><a href="/document/edit/${i.id}/">${i.code}</a></td>
                <td>${i.creation_date}</td>
                <td>${i.status.name}</td>
                <td>${i.product ? i.product.start_date: ''}</td>
                <td style="white-space: nowrap">${i.product ? Format.formatCurrency(i.product.value) : ''}
                <td style="white-space: nowrap">${i.product ? Format.formatCurrency(i.product.capital_net) : ''}</td>
            </tr>
            `
        }



        table.appendChild(thead);
        table.appendChild(tbody);

        container.appendChild(table);
    }

    _renderProducts() {
        if (!this.productsContainer) {
            return;
        }

        let container = jsUtils.Utils.domElement('div');

        let data = jsUtils.Utils.domElement('div', null, 'widget-user-details-product-data');
        container.appendChild(data);

        this.productsContainer.appendChild(container);

        if (!this.data.products.length) {
            data.innerText = 'brak produktów';
            return;
        }

        let table = jsUtils.Utils.domElement('table', '', 'table');
        let thead = jsUtils.Utils.domElement('thead', '', 'table');
        let tbody = jsUtils.Utils.domElement('tbody');

        thead.innerHTML = `
                <tr>
                    <th>Nr umowy</th>
                    <th>data rozpoczęcia</th>
                    <th>Wartość</th>  
                    <th>Status</th>
                </tr>
            `;

        tbody.innerHTML = '';

        for (let i of this.data.products) {
            tbody.innerHTML += `
            <tr>
                <td>${i.agreement_no}</td>
                <td>${i.start_date}</td>
                <td>${Format.formatCurrency(i.value)}</td>
                <td>${i.status.name}</td>
            </tr>
            `
        }

        for (let i of this.data.products) {
            tbody.innerHTML += `
            <tr>
                <td>${i.agreement_no}</td>
                <td>${i.start_date}</td>
                <td>${Format.formatCurrency(i.value)}</td>
                <td>${i.status.name}</td>
            </tr>
            `
        }

        table.appendChild(thead);
        table.appendChild(tbody);

        data.appendChild(table);

    }

    _renderPersonalData() {
        let table = jsUtils.Utils.domElement('table', '', 'table');
        let tbody = jsUtils.Utils.domElement('tbody');
        tbody.innerHTML = `
            <tr><td><span class="widget-user-details-field-icon"><i class="fas fa-envelope"></i></span>E-mail</td><td>${jsUtils.Utils.nullValue(this.data.user.email, '-')}</td>
            <tr><td><span class="widget-user-details-field-icon"><i class="fas fa-phone"></i></span>Telefon</td>
            <td><a href="#">${jsUtils.Utils.nullValue(this.data.user.phone_one, '-')}</a></td>
            <tr><td><span class="widget-user-details-field-icon"><i class="fas fa-tag"></i></span>Tagi</td><td>
                <div class="widget-user-details-tag-container">${this._renderTags()}</div></td></tr>
            <tr><td><span class="widget-user-details-field-icon"><i class="fas fa-thermometer-half"></i></span>Status</td><td>${this.data.user.status}</td></tr>   
        `;
        table.appendChild(tbody);
        this.personalDataContainer.appendChild(table);
    }

    render(id) {
        this.reset();
        this.getDetails(id, this.url).then((data) => {
            this.data = data;
            this._renderNotes(id);
            this._renderHeader();
            // this._renderProducts();
            this._renderEvents();
            this._renderDocuments();
            this.calendarOpts.invited_users = [
                {id: _g.credentials.user.id, first_name: _g.credentials.user.first_name, last_name: _g.credentials.user.last_name},
                {id: this.data.user.id, first_name: this.data.user.first_name, last_name: this.data.user.last_name}
            ];

            $(this.modal).modal();
        });
    }
}

export {
    UserDetails
}