import "../scss/product-dashboard.scss";
import {SystemException} from "../../../../../_core/exception";
import {Format} from "../../../../../_core/format/format";
import ajaxCall from "../../../../../_core/ajax";

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

        this.balancePerDayProductStartDate = document.getElementById('balancePerDayProductStartDate');

        this.balancePerDayContainer = document.getElementById('balancePerDayContainer');
        this.balancePerDayDetailContainer = document.getElementById('balancePerDayDetailContainer');
        this.balancePerDayModal = document.getElementById('balancePerDayModal')
        this.balancePerDayDate = document.getElementById('balancePerDayDate');
        this.balanceValidToDate = document.getElementById('balanceValidToDate');
        this.balancePerDayEmulatePayment = document.getElementById('balancePerDayEmulatePayment');

        this.balancePerDayValue = document.getElementById('balancePerDayValue');
        this.balancePerDayCapitalNotRequired = document.getElementById('balancePerDayCapitalNotRequired');
        this.balancePerDayCapitalRequired = document.getElementById('balancePerDayCapitalRequired');
        this.balancePerDayCapitalTotal = document.getElementById('balancePerDayCapitalTotal');
        this.balancePerDayRequiredLiabilities = document.getElementById('balancePerDayRequiredLiabilities');

        this.balancePerDayInterestRequired = document.getElementById('balancePerDayInterestRequired');
        this.balancePerDayInterestDaily = document.getElementById('balancePerDayInterestDaily');
        this.balancePerDayInterestCumulatedPerDay = document.getElementById('balancePerDayInterestCumulatedPerDay');
        this.balancePerDayInterestNominalCumulatedPerDay = document.getElementById('balancePerDayInterestNominalCumulatedPerDay');
        this.balancePerDayInterestForDelayCumulatedPerDay = document.getElementById('balancePerDayInterestForDelayCumulatedPerDay');
        this.balancePerDayInterestForDelayMaxCumulatedPerDay = document.getElementById('balancePerDayInterestForDelayMaxCumulatedPerDay');

        this.balancePerDayInterestNominalEndDate = document.getElementById('balancePerDayInterestNominalEndDate');
        this.balancePerDayInterestForDelayStartDate = document.getElementById('balancePerDayInterestForDelayStartDate');
        this.balancePerDayInterestForDelayMaxStartDate = document.getElementById('balancePerDayInterestForDelayMaxStartDate');

        this.balancePerDayCostTotal = document.getElementById('balancePerDayCostTotal');
        this.balancePerDayCostVindicationFee = document.getElementById('balancePerDayCostVindicationFee');
        this.balancePerDayCostContractualPenalty = document.getElementById('balancePerDayCostContractualPenalty');
        this.balancePerDayInstalmentTotal = document.getElementById('balancePerDayInstalmentTotal');

        this.init();
    }


    formatDecimal(value, small = false) {
        let val = Format.formatCurrency(value).split(','); // value.toString().split('.');
        return `<span class="product-dashboard-decimal-integer${small ? '-small' : ''} product-dashboard-font-stretched">${val[0]},</span><span class="product-dashboard-decimal-fractional${small ? '-small' : ''} product-dashboard-font-stretched ">${val[1]}</span>`;
    }

    clearBalancePerDayContainer() {
        for (let i of document.querySelectorAll('#balancePerDayContainer table span')) {
            i.innerText = '';
        }
        this.balancePerDayDate.value = null;
        this.balancePerDayValue.innerText = '';

        this.balancePerDayDetailContainer.style.visibility = 'hidden'

    }

    bindData() {
        if (this.data && typeof this.data == 'object') {
            let html = this.template;
            html = html.replace('__START_DATE__', this.data.startDate);
            html = html.replace('__STATUS__', this.data.status);
            html = html.replace('__BALANCE__', this.formatDecimal(this.data.balance));
            html = html.replace('__INTEREST_REQUIRED__', this.formatDecimal(this.data.interest_per_day));
            html = html.replace('__COST_TOTAL__', this.formatDecimal(this.data.cost_total));
            html = html.replace('__INSTALMENT_TOTAL__', this.formatDecimal(this.data.instalment_total));

            html = html.replace('__CAPITAL_REQUIRED__', this.formatDecimal(this.data.capital_required, true));
            html = html.replace('__CAPITAL_NOT_REQUIRED__', this.formatDecimal(this.data.capital_not_required, true));
            html = html.replace('__REQUIRED_LIABILITIES_SUM__', this.formatDecimal(this.data.required_liabilities_sum, true));

            html = html.replace('__INTEREST_TOTAL__', this.formatDecimal(this.data.interest_cumulated_per_day, true));
            html = html.replace('__INTEREST_REQUIRED_DAILY__', this.formatDecimal(this.data.interest_daily, true));
            html = html.replace('__INTEREST_RATE__', this.formatDecimal(this.data.interest_rate, true));

            html = html.replace('__COST__', this.formatDecimal(this.data.cost, true));

            html = html.replace('__INSTALMENT_COUNT__', this.data.instalmentCount);
            html = html.replace('__INSTALMENT_MC_SUM__', this.formatDecimal(this.data.instalmentMcSum, true));
            html = html.replace('__INSTALMENT_BALLOON__', this.formatDecimal(this.data.instalmentBalloon, true));
            html = html.replace('__PAYMENT_COUNT__', this.data.paymentCount);

            this.container.innerHTML = html;
        }
        // $("#balanceDatepicker").datetimepicker({
        //     locale: "pl",
        //     inline: true,
        //     format: 'YYYY-MM-DD'
        // });

        let getBalance = () => {
            ajaxCall({
                    method: 'get',
                    url: '/product/api/balance-per-day/',
                    data: {
                        id: this.id,
                        balanceDate: this.balancePerDayDate.value,
                        emulatePayment: this.balancePerDayEmulatePayment.checked
                    }
                },
                (resp) => {
                    this.balancePerDayProductStartDate.value = resp.product_start_date;

                    this.balancePerDayValue.innerText = Format.formatCurrency(resp.balance);

                    this.balancePerDayCapitalNotRequired.innerText = Format.formatCurrency(resp.capital_not_required);
                    this.balancePerDayCapitalRequired.innerText = Format.formatCurrency(resp.capital_required);
                    this.balancePerDayCapitalTotal.value = Format.formatCurrency(resp.capital_total);
                    this.balancePerDayRequiredLiabilities.innerText = Format.formatCurrency(resp.current_liabilities);

                    this.balancePerDayInterestCumulatedPerDay.innerText = Format.formatCurrency(resp.interest_cumulated_per_day);
                    this.balancePerDayInterestNominalCumulatedPerDay.innerText = Format.formatCurrency(resp.interest_nominal_cumulated_per_day);
                    this.balancePerDayInterestForDelayCumulatedPerDay.innerText = Format.formatCurrency(resp.interest_for_delay_cumulated_per_day);
                    this.balancePerDayInterestForDelayMaxCumulatedPerDay.innerText = Format.formatCurrency(resp.interest_for_delay_max_cumulated_per_day);
                    this.balancePerDayInterestRequired.innerText = Format.formatCurrency(resp.interest_required);
                    this.balancePerDayInterestDaily.innerText = Format.formatCurrency(resp.interest_daily);

                    this.balancePerDayInterestNominalEndDate.value = resp.interest_nominal_end_date;
                    this.balancePerDayInterestForDelayStartDate.value = resp.interest_for_delay_date;
                    this.balancePerDayInterestForDelayMaxStartDate.value = resp.interest_for_delay_max_date;

                    this.balancePerDayCostVindicationFee.innerText = Format.formatCurrency(resp.cost_aggregation.COST_VINDICATION_FEE);
                    this.balancePerDayCostContractualPenalty.innerText = Format.formatCurrency(resp.cost_aggregation.COST_CONTRACTUAL_PENALTY);
                    this.balancePerDayCostTotal.innerText = Format.formatCurrency(resp.cost_total);

                    this.balancePerDayInstalmentTotal.innerText = Format.formatCurrency(resp.instalment_total);

                    this.balancePerDayDetailContainer.style.visibility = 'visible'
                }
            )
        }

        this.balancePerDayDate.addEventListener('change', (e) => {
                getBalance();
            }
        );

        this.balancePerDayEmulatePayment.addEventListener('change', (e) => {
                getBalance();
            }
        );

        document.querySelector('.show-balance-per-day').addEventListener('click', (e) => {
            this.clearBalancePerDayContainer();
            $(this.balancePerDayModal).modal();
        });
    }

    printBalancePerDay() {
        if (!this.balancePerDayDate.value) {
            Alert.warning('Brak daty salda');
            return;
        }
        report.generate(
            false,
            true,
            'BALANCE_PER_DAY_V2',
            _g.product.document.id,
            {
                balancePerDayReportType: document.querySelector("input[name='balancePerDayReportType']:checked").value,
                balancePerDayDate: this.balancePerDayDate.value,
                balanceValidToDate: this.balanceValidToDate.value,
                balancePerDayCapitalRequired: this.balancePerDayCapitalRequired.innerText,
                balancePerDayCapitalNotRequired: this.balancePerDayCapitalNotRequired.innerText,
                balancePerDayInterestNominalCumulatedPerDay: this.balancePerDayInterestNominalCumulatedPerDay.innerText,
                balancePerDayInterestCumulatedPerDay: this.balancePerDayInterestCumulatedPerDay.innerText,
                balancePerDayInterestForDelayCumulatedPerDay: this.balancePerDayInterestForDelayCumulatedPerDay.innerText,
                balancePerDayInterestForDelayMaxCumulatedPerDay: this.balancePerDayInterestForDelayMaxCumulatedPerDay.innerText,
                balancePerDayInterestRequired: this.balancePerDayInterestRequired.innerText,
                balancePerDayCostContractualPenalty: this.balancePerDayCostContractualPenalty.innerText,
                balancePerDayCostVindicationFee: this.balancePerDayCostVindicationFee.innerText,
                balancePerDayCostTotal: this.balancePerDayCostTotal.innerText,
                balancePerDayValue: this.balancePerDayValue.innerText,
                balancePerDayInterestDaily: this.balancePerDayInterestDaily.innerText,
                balancePerDayProductStartDate: this.balancePerDayProductStartDate.value,
                balancePerDayInterestNominalEndDate: this.balancePerDayInterestNominalEndDate.value,
                balancePerDayInterestForDelayStartDate: this.balancePerDayInterestForDelayStartDate.value,
                balancePerDayInterestForDelayMaxStartDate: this.balancePerDayInterestForDelayMaxStartDate.value,
                balancePerDayCapitalTotal: this.balancePerDayCapitalTotal.value,
                balancePerDayRequiredLiabilities: this.balancePerDayRequiredLiabilities.innerText
            },
            {
                'product_id': _g.product.id
            });
    }

    init() {
        this.balancePerDayModal.querySelector('.btn-print-balance').addEventListener('click', e => {
            this.printBalancePerDay();

        });
    }
}

export {ProductDashboard};