import {InstalmentSchedule} from "./instalment-schedule";
import {Toolbar} from "../../../../_core/containers/toolbar";
import {isSaved} from "../../../../_core/core";
import ajaxCall from "../../../../_core/ajax";

const className = 'ProductInstalmentSchedule';

class ProductInstalmentSchedule extends InstalmentSchedule {
    constructor(rowContainer, idDocument, customMapping = null, opts = null) {
        super(rowContainer, idDocument, customMapping, opts);
        this.instalmentScheduleUrl = "/product/api/instalment-schedule/";
        this.toolbar = new Toolbar(this.rowContainer.closest('.panel').querySelector('.panel-heading'));

        this.toolbar.addButton(null,
            '',
            'fa fa-print',
            'Drukuj harmonogram',
            () => {
                if (isSaved('Przed wygenerowaniem harmonogramu należy zapisać zmiany')) {
                    this.printSchedule(_g.product.id);
                }
            },
            null);
    }

    printSchedule(id, template = 'SCHEDULE') {
        $(".loader-container").fadeIn();

        ajaxCall({
                method: 'post',
                url: '/report/api/',
                data: {
                    documentId: _g.product.document.id,
                    templateCode: template,
                    queryParams: `{"product_id":"${id}"}`
                }
            },
            (res) => {
                window.core.downloadReport(res.reportId);
            },
            (res) => {
                console.error(res.responseJSON);
                window.Alert.error(res.responseJSON.errmsg);
            },
            () => {
                $(".loader-container").fadeOut();
            }
        );
    }

    displayErrors(errMsg, reset = true) {
        Alert.error('Błąd', errMsg);
        //    todo: revert changes
    }

    cleanErrors() {
    }

    reset(rows = 0, callback = null) {
    }

    getRow(idx) {
        return this.rowContainer.rows[idx];
    }

    addRow(data) {
    }

    updateRow(idx, data) {
        let row = this.getRow(idx);
        if (!row) {
            return;
        }

        for (const [k, v] of Object.entries(data)) {
            let el = row.querySelector(`[data-code="${k}"]`);
            Input.setValue(el, v.value);
        }
    }

    getErrorContainer() {
        return null;
    }

    _getScheduleItemsIds() {
        this.mappingIds['instalment-maturity-date'] = {code: 'maturity_date', htmlId: 'id_product-schedule-{prefix}-maturity_date'};
        this.mappingIds['instalment-capital'] = {code: 'instalment_capital', htmlId: 'id_product-schedule-{prefix}-instalment_capital'};
        this.mappingIds['instalment-commission'] = {code: 'instalment_commission', htmlId: 'id_product-schedule-{prefix}-instalment_commission'};
        this.mappingIds['instalment-interest'] = {code: 'instalment_interest', htmlId: 'id_product-schedule-{prefix}-instalment_interest'};
        this.mappingIds['instalment-total'] = {code: 'instalment_total', htmlId: 'id_product-schedule-{prefix}-instalment_total'};
    }

    init() {
        this._initSchedule();

        // handling internal changes (schedule row items change)
        this.rowContainer.addEventListener('change', e => {
            this._handleChange(e.target);
        });

        $(this.rowContainer).on('dp.change', e => {
            this._handleChange(e.target);
        });

        this.setInstalmentInterestRateCallback(() => {
            let _instalmentInterestRate = {};
            _instalmentInterestRate[_g.settings.MINUS_INFINITY_DATE] = _g.product.instalmentInterestRate;

            for (let i of Array.from(document.querySelectorAll('#product-interest-formset-table tbody tr'))) {
                if (i.querySelector('div.delete-indicator input[type="hidden"]')?.value) {
                    continue;
                }
                let startDate = Input.getValue(i.querySelector('[data-code="interest_start_date"]'));
                let rate = Input.getValue(i.querySelector('[data-code="interest_statutory_rate"]'));

                if (startDate && rate) {
                    _instalmentInterestRate[startDate] = (rate / 100).toFixed(4);
                } else {
                    throw 'No valid startDate end/or rate of instalment interest';
                }
            }
            return _instalmentInterestRate;
        });
    }
}

export {ProductInstalmentSchedule};
