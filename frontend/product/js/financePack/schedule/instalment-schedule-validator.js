import {SystemException} from "../../../../_core/exception";
import {INSTALMENT_CAPITAL_SELECTOR, INSTALMENT_COMMISSION_SELECTOR, INSTALMENT_MATURITY_DATE_SELECTOR} from "./instalment-schedule";

const className = 'ScheduleValidator';

class InstalmentScheduleValidator {
    constructor(rowContainer, capitalNet, commission, startDate, isStatic = false) {
        this.rowContainer = rowContainer;
        this.capitalNet = capitalNet;
        this.commission = commission;
        this.startDate = startDate;
        this.isStatic = isStatic;

        this.init();
    }

    static validateInstalmentDate(el, startDate, checkNeighboursNotNull = false) {
        let dt = Input.getValue(el, null);
        if (!dt) {
            throw new SystemException(`[${className}][validateInstalmentDate]: Data wymagalności nie może być pusta.`);
        }

        try {
            dt = new Date(dt);
        } catch (ex) {
            throw new SystemException(`[${className}][validateInstalmentDate]: ${ex}`);
        }

        let idx = 0;
        let maturityDateSet = Array.from(el.closest('tbody').querySelectorAll(`tr input${INSTALMENT_MATURITY_DATE_SELECTOR}`));
        for (let i of maturityDateSet) {
            if (i === el) {
                break;
            }
            idx++;
        }

        let previousDate = startDate ? startDate : new Date('0000-01-01');
        let nextDate = new Date('9999-01-01');
        if (idx) {
            let previousDateValue = maturityDateSet[idx - 1].value;
            if (checkNeighboursNotNull && !previousDateValue) {
                throw new SystemException(`Data poprzedniej raty nie może być pusta.`);
            }

            if (previousDateValue) {
                previousDate = new Date(previousDateValue);
            }
        }
        if ((idx + 1) < maturityDateSet.length) {
            let nextDateValue = maturityDateSet[idx + 1].value;
            if (checkNeighboursNotNull && !nextDateValue) {
                throw new SystemException(`Data następnej raty nie może być pusta.`);
            }
            if (nextDateValue) {
                nextDate = new Date(nextDateValue);
            }
        }
        if (previousDate >= dt || nextDate <= dt) {
            throw new SystemException(
                `Wartość daty musi zawierać się w przedziale:<br>
                    (${moment(previousDate).format('YYYY-MM-DD')}: ${moment(nextDate).format('YYYY-MM-DD')})`);
        }
    }

    static validateInstalmentSum(container, capitalNet, commission) {
        let instalmentCapitalSum = 0;
        let instalmentCommissionSum = 0;

        if (!container) {
            throw new SystemException(`[${className}][validateInstalmentSum]: brak kontenera harmonogramu.`);
        }

        let instalments = Array.from(container.querySelectorAll('tr'));

        for (let i of instalments) {
            if (i === instalments[instalments.length - 1]) {
                break;
            }
            // instalment n - 1 sums calculating
            instalmentCapitalSum += parseFloat(Input.getValue(i.querySelector(INSTALMENT_CAPITAL_SELECTOR), 0));
            instalmentCommissionSum += parseFloat(Input.getValue(i.querySelector(INSTALMENT_COMMISSION_SELECTOR), 0));
        }

        // instalment sums validation
        if (instalmentCapitalSum > capitalNet) {
            throw new SystemException(`Suma rat kapitałowych nie może przewyższać wartości kapitału netto.<br/>Jest: ${instalmentCapitalSum}, powinno być max: ${capitalNet}`);
        }
        if (instalmentCommissionSum > commission) {
            throw new SystemException(`Suma rat prowizyjnych nie może przewyższać wartości całkowitej prowizji<br/>Jest: ${instalmentCommissionSum}, powinno być max: ${commission}`);
        }
    }

    validate(el) {
        if (el.classList.contains(INSTALMENT_MATURITY_DATE_SELECTOR.substr(1))) {
            InstalmentScheduleValidator.validateInstalmentDate(el, this.startDate);
        } else {
            InstalmentScheduleValidator.validateInstalmentSum(
                this.rowContainer,
                this.isStatic ? this.capitalNet : parseInt(Input.getValue(this.capitalNet, 0)),
                this.isStatic ? this.commission : parseInt(Input.getValue(this.commission, 0))
            )
        }
    }

    init() {
        try {
            let startDateValue = this.isStatic ? this.startDate : document.getElementById(this.startDate)?.value;
            if (startDateValue) {
                this.startDate = new Date(startDateValue);
            }


        } catch (ex) {
            throw new SystemException(`[${className}][init]: ${ex}`);
        }
    }
}

export {InstalmentScheduleValidator};