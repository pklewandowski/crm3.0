import "../scss/product-dashboard.scss";
import {SystemException} from "../../../../../_core/exception";
import {Format} from "../../../../../_core/format/format";

const className = 'ProductDashboard';

class ProductDashboard {
    constructor(id, container, templateId, data) {
        this.calcDate = null;

        if (!id) {
            throw new SystemException(`${className}: No product id`);
        }
        this.id = id;

        if (!templateId) {
            throw new SystemException(`${className}: No template id`);
        }
        this.template = document.getElementById(templateId).innerHTML;

        if (!container) {
            throw new SystemException(`${className}: No container`);
        }
        this.container = typeof container === 'object' ? container : document.getElementById(container);
        if (!container) {
            throw new SystemException(`${className}: Couldn't find container by id`);
        }

        // there can be no data, when it's the first day of product. todo: what if so?
        this.data = data;

        this.init();
    }


    formatDecimal(value, small = false) {
        let val = Format.formatCurrency(value).split(','); // value.toString().split('.');
        return `<span class="product-dashboard-decimal-integer${small ? '-small' : ''} product-dashboard-font-stretched">${val[0]},</span><span class="product-dashboard-decimal-fractional${small ? '-small' : ''} product-dashboard-font-stretched ">${val[1]}</span>`;
    }

    bindData() {
        if (this.data && typeof this.data == 'object') {
            let html = this.template;
            html = html.replace('__START_DATE__', this.data.startDate);
            html = html.replace('__STATUS__', this.data.status);
            html = html.replace('__BALANCE__', this.formatDecimal(this.data.balance));
            html = html.replace('__INTEREST_FOR_DELAY_REQUIRED__', this.formatDecimal(this.data.interest_for_delay_required));
            html = html.replace('__COST_TOTAL__', this.formatDecimal(this.data.cost_total));
            html = html.replace('__INSTALMENT_TOTAL__', this.formatDecimal(this.data.instalment_total));

            html = html.replace('__CAPITAL_REQUIRED__', this.formatDecimal(this.data.capital_required, true));
            html = html.replace('__CAPITAL_NOT_REQUIRED__', this.formatDecimal(this.data.capital_not_required, true));
            html = html.replace('__REQUIRED_LIABILITIES_SUM__', this.formatDecimal(this.data.required_liabilities_sum, true));

            html = html.replace('__INTEREST_FOR_DELAY_TOTAL__', this.formatDecimal(this.data.interest_for_delay_total, true));
            html = html.replace('__INTEREST_FOR_DELAY_REQUIRED_DAILY__', this.formatDecimal(this.data.interest_for_delay_required_daily, true));
            html = html.replace('__INTEREST_FOR_DELAY_RATE__', this.formatDecimal(this.data.interest_for_delay_rate, true));

            html = html.replace('__COST__', this.formatDecimal(this.data.cost, true));

            html = html.replace('__INSTALMENT_COUNT__', this.data.instalmentCount);
            html = html.replace('__INSTALMENT_MC_SUM__', this.formatDecimal(this.data.instalmentMcSum, true));
            html = html.replace('__INSTALMENT_BALLOON__', this.formatDecimal(this.data.instalmentBalloon, true));
            html = html.replace('__PAYMENT_COUNT__', this.data.paymentCount);

            this.container.innerHTML = html;
        }
    }

    init() {
    }

}

export {ProductDashboard};