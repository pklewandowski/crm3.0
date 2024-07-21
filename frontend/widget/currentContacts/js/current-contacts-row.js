import {ToolbarUtils} from "../../../_core/utils/toolbar-utils";
import {getPersonalTitle} from "../../../user/js/utils";


const rowTemplate = `
        __DOT__
        <div class="widget-current-contacts-row-content">
             <div class="widget-current-contacts-name">__NAME__</div>
             <div class="widget-current-contacts-title">__TITLE__</div>
        </div>
        <div class="widget-current-contacts-row-overdue-days">
            __OVERDUE_DAYS__
        </div>
`;

class CurrentContactsRow {
    static _getOverdueColor(days) {
        if (!days) {
            return 'widget-current-contacts-red-dot';
        }
        if (days >= 0) {
            return 'widget-current-contacts-green-dot';
        }

        else if (days > -14) {
            return 'widget-current-contacts-yellow-dot';
        }

        return 'widget-current-contacts-red-dot';
    }


    static _renderCloseEventBtn() {
        let closeEventBtn = ToolbarUtils.closeBtn();
        closeEventBtn.classList.add('widget-current-contacts-close-event');
        return closeEventBtn;
    }

    static _renderColorDot(rowData) {
        let divColorDot;
        if (!rowData.max_event_date) {
            divColorDot = jsUtils.Utils.domElement('i', null, ['fas', 'fa-exclamation-circle', 'type-color-dot']);

        } else {
            divColorDot = jsUtils.Utils.domElement('div', null, 'type-color-dot');
        }

        divColorDot.classList.add(this._getOverdueColor(rowData.date_diff));
        let div = jsUtils.Utils.domElement('div');
        div.appendChild(divColorDot);
        return div;
    }

    static render(rowData) {

        let li = jsUtils.Utils.domElement('li', '', 'widget-current-contacts-row-container');
        li.dataset['id'] = rowData.user.id;
        let dot = CurrentContactsRow._renderColorDot(rowData).innerHTML;

        let html = rowTemplate;
        html = html.replace('__OVERDUE_DAYS__', rowData.max_event_date ? rowData.date_diff : '');
        html = html.replace('__NAME__', getPersonalTitle(rowData.user));
        html = html.replace('__TITLE__', rowData.max_event_date ? rowData.max_event_date : 'brak kontaktu');
        html = html.replace('__DOT__', dot);
        li.innerHTML = html;

        // let contentContainer = jsUtils.Utils.domElement('div', null, 'widget-current-contacts-content-container');
        // li.appendChild(contentContainer);
        //
        // li.dataset['id'] = rowData.user.id;
        //
        // let overdueDays = jsUtils.Utils.domElement('div', null, 'widget-current-contacts-overdue-days');
        // overdueDays.innerText = rowData.max_event_date ? rowData.date_diff : '';
        //
        //li.contentContainer(CurrentContactsRow._renderColorDot(rowData));
        // li.contentContainer(overdueDays);
        //
        // let div = jsUtils.Utils.domElement('div', '', 'widget-current-contacts-name');
        //
        // div.innerHTML = getPersonalTitle(rowData.user);
        // // `<strong>${rowData.user.first_name ? rowData.user.first_name: ''} ${rowData.user.last_name?rowData.user.last_name: ''} ${rowData.user.company_name?rowData.user.company_name: ''}</strong>`;
        // contentContainer.appendChild(div);
        //
        // let title = jsUtils.Utils.domElement('div', null, 'widget-current-contacts-title');
        // title.innerText = rowData.max_event_date ? rowData.max_event_date : 'brak kontaktu';
        //
        // contentContainer.appendChild(title);

        return li;
    }
}

export {CurrentContactsRow};