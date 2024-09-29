import ajaxCall from "../../_core/ajax";

class Address {
    constructor(modalId) {
        this.modal = document.getElementById(modalId);
        this.historyDataRowTemplate =
            '<tr>' +
            '<td>__HISTORY_DATE__</td>' +
            '<td>__HISTORY_USER__</td>' +
            '<td>__STREET__</td>' +
            '<td>__STREET_NO__</td>' +
            '<td>__APARTMENT_NO__</td>' +
            '<td>__POST_CODE__</td>' +
            '<td>__CITY__</td>' +
            '<td>__COUNTRY__</td>' +
            '<td><a class="btn btn-default"><i class="fas fa-history"></i></a></td>' +
            '</tr>';
        this.container = this.modal ? this.modal.querySelector('.historyDataContainer') : null;
    }

    fillHistoryTable(hData) {
        if (!this.container) {
            return;
        }
        for (let i of hData) {
            let row = jsUtils.Utils.domElement('tr');
            row.innerHTML = this.historyDataRowTemplate
                .replace('__HISTORY_DATE__', i.history_date)
                .replace('__HISTORY_USER__', `${i.history_user.first_name} ${i.history_user.last_name}`)
                .replace('__STREET__', i.street)
                .replace('__STREET_NO__', i.street_no)
                .replace('__APARTMENT_NO__', i.apartment_no)
                .replace('__POST_CODE__', i.post_code)
                .replace('__CITY__', i.city)
                .replace('__COUNTRY__', i.country);
            this.container.appendChild(row);
        }
    }

    revertAddressFromHistory(e) {
        let tr = e.closest('tr');
        for(let i of Array.from(tr.querySelector('td'))){
        // todo: finish
        }
    }

    getHistory(addressId) {
        if (!this.container) {
            return;
        }
        ajaxCall(
            {
                method: 'get',
                url: '/address/api/history/',
                data: {addressId: addressId}
            },
            (resp) => {
                this.container.innerHTML = null;
                this.fillHistoryTable(resp);
                $(this.modal).modal();

            },
            (resp) => {
                Alert.error('Błąd', resp.responseJSON.errmsg);
                jsUtils.LogUtils.log(resp.responseJSON);
            }
        )
    }
}

export default Address;