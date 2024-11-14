import ajaxCall from "../../../../_core/ajax";
import Alert from "../../../../_core/alert";
import {SystemException} from "../../../../_core/exception";
import {InstalmentScheduleValidator} from "./instalment-schedule-validator";
import {ToolbarUtils} from "../../../../_core/utils/toolbar-utils";
import {Format} from "../../../../_core/format/format";

const className = 'InstalmentSchedule';
const SCHEDULE_MAPPING_URL = '/product/api/instalment-schedule/mapping';

const INSTALMENT_NUMBER_SELECTOR = '.instalment-number';
const INSTALMENT_MATURITY_DATE_SELECTOR = '.instalment-maturity-date';
const INSTALMENT_CAPITAL_SELECTOR = '.instalment-capital';
const INSTALMENT_COMMISSION_SELECTOR = '.instalment-commission';
const INSTALMENT_INTEREST_SELECTOR = '.instalment-interest';
const INSTALMENT_TOTAL_SELECTOR = '.instalment-total';

class InstalmentSchedule {
    constructor(rowContainer, idDocument, customMapping = null, opts = null) {
        if (!idDocument) {
            throw new SystemException(`[${className}][constructor]: brak id dokumentu`);
        }

        // todo: finally get the url form external (like conf or _g)
        this.instalmentScheduleUrl = "/product/api/instalment-schedule/";
        this.instalmentInterestRateCallback = null;

        let _instalmentInterestRate = {};
        _instalmentInterestRate[_g.settings.MINUS_INFINITY_DATE] = 0;

        this.scheduleParamsDefaults = {
            startDate: null, // mapped START_DATE
            capitalNet: 0, // mapped CAPITAL_NET
            value: 0, // total product value mapped VALUE
            commission: 0, //mapped COMMISSION
            instalmentNumber: 0, // mapped INSTALMENT_NUMBER
            instalmentCapital: 0, // mapped INSTALMENT_CAPITAL
            instalmentTotal: 0, // mapped INSTALMENT_TOTAL
            instalmentCommission: 0, // mapped INSTALMENT_COMMISSION
            constantInstalment: '', // mapped CONSTANT_INSTALMENT
            arbitraryInstalment: '', // mapped ARBITRARY_INSTALMENT
            instalmentInterestRate: _instalmentInterestRate, // mapped INSTALMENT_INTEREST_RATE
            instalmentInterestCapitalTypeCalcSource: 'N' // mapped INSTALMENT_INTEREST_CAPITAL_TYPE_CALC_SOURCE 'N' // 'N' - net, 'V' - value
        };
        this.rowContainer = rowContainer;
        this.idDocument = idDocument;

        this.aggregates = null;
        /**
         * opts
         * opts are used for generating schedule "statically" that means for given exact values. In this case there is no dynamic generating.
         * No external changes handling.
         * Only changes inside schedule data are processed (like particular row instalment change etc.)
         */
        this.opts = null;

        if (opts) {
            this.opts = Object.assign({}, this.scheduleParamsDefaults, opts);
        }

        /**
         * mapping
         * It's used in case when there's a need to generate schedule dynamically just according to changes made by user
         * on the external to schedule table data, like ie. change loan start date in the document attribute form
         * or change commission/capital instalment etc.
         * There can be multiple schedules in the document. So mapping may differ for given schedules.
         * if customMapping is set, then custom mapping is processed
         * @type {{}}
         */
        this.mapping = {};
        this.customMapping = customMapping;
        this.mappingIds = {};
        this.validator = null;

        this.events = {
            scheduleRefresh: 'scheduleSectionEvt:refresh',
            scheduleCreated: 'scheduleSectionEvt:created'
        };

        this.init();
    }

    setInstalmentInterestRateCallback(callback) {
        if (typeof callback === 'function') {
            this.instalmentInterestRateCallback = callback;
        }
    }

    displayErrors() {
        throw new SystemException(`[${this.constructor.name}][displayErrors]: not implemented`);
    }

    cleanErrors() {
        throw new SystemException(`[${this.constructor.name}][displayErrors]: not implemented`);
    }

    reset(rows = 0, callback = null) {
        throw new SystemException(`[${this.constructor.name}][reset]: not implemented`);
    }

    getRowsLength() {
        return this.rowContainer.querySelectorAll('tr').length;
    }

    getRow(idx) {
        throw new SystemException(`[${this.constructor.name}][getRow]: not implemented`);
    }

    getLastRow() {
        throw new SystemException(`[${this.constructor.name}][getLastRow]: not implemented`);
    }

    addRow(data) {
        throw new SystemException(`[${this.constructor.name}][addRow]: not implemented`);
    }

    updateRow(idx, data) {
        throw new SystemException(`[${this.constructor.name}][updateRow]: not implemented`);
    }

    getRowIdx(el) {
        return (el.closest('tr').sectionRowIndex);
    }

    getErrorContainer() {
        throw new SystemException(`[${this.constructor.name}][getErrorContainer]: not implemented`);
    }

    _setLastRowReadOnly(el) {
        Input.setAttribute(el.querySelector(INSTALMENT_CAPITAL_SELECTOR), {name: 'readOnly', value: 'readonly'});
        Input.setAttribute(el.querySelector(INSTALMENT_INTEREST_SELECTOR), {name: 'readOnly', value: 'readonly'});
        Input.setAttribute(el.querySelector(INSTALMENT_COMMISSION_SELECTOR), {name: 'readOnly', value: 'readonly'});
        Input.setAttribute(el.querySelector(INSTALMENT_TOTAL_SELECTOR), {name: 'readOnly', value: 'readonly'});
    }

    _renderScheduleSections(res) {
        let row = null;
        let valueWithInterest = 0;
        let interestTotal = 0;

        for (let [idx, rowData] of res.entries()) {
            let mappedData = {};

            for (let [k, v] of Object.entries(rowData)) {
                if (this.mappingIds[k]?.code) {
                    mappedData[this.mappingIds[k].code] = {value: v, meta: {}};
                }
            }
            row = this.getRow(idx);

            if (row) {
                this.updateRow(idx, mappedData);

            } else {
                row = this.addRow(mappedData);
            }

            valueWithInterest += rowData['instalment-total'];
            interestTotal += rowData['instalment-interest'];

            if (this.opts?.startDate || this.mapping?.startDate?.item) {
                let startDate = this.opts?.startDate ? this.opts.startDate : this._getMappingValue('startDate');
                let maturityDate = row.querySelector(INSTALMENT_MATURITY_DATE_SELECTOR);

                if (maturityDate) {
                    if (Input.isNullValue(startDate)) {
                        maturityDate.setAttribute('disabled', 'disabled');
                        Input.setValue(maturityDate, null);

                    } else {
                        maturityDate.removeAttribute('disabled');
                        if (idx) {
                            this.setMinDate(maturityDate, idx - 1);

                        } else {
                            maturityDate.minDate(new Date(startDate).addDays(1).defaultFormat());
                        }
                    }
                }
            }
        }

        if (row) {
            this._setLastRowReadOnly(row);
        }

        if (this.mapping?.valueWithInterest?.item) {
            Input.setValue(this.mapping.valueWithInterest.item, valueWithInterest.toFixed(2));
        }

        if (this.mapping?.interestTotal?.item) {
            Input.setValue(this.mapping.interestTotal.item, interestTotal.toFixed(2));
        }

        // remove all rows over the instalment number (if exist) - this is necessary when instalment number specified
        // is lower than previous one
        let rows = this.getRowsLength();
        let newRows = res.length;
        if (rows > newRows) {
            for (let i = newRows; i < rows; i++) {
                this.getLastRow().remove();
            }
        }
    }

    _renderAggregates(aggregates) {
        this.aggregates = aggregates;
        this.rowContainer.append(
            <tr className="instalment-schedule-aggregates">
                <td></td>
                <td></td>
                <td className="instalment-capital-aggregate">
                    <div className="form-control input-format-currency">{aggregates.instalment_capital_aggregate}</div>
                </td>
                <td className="instalment-interest-aggregate">
                    <div className="form-control input-format-currency">{aggregates.instalment_interest_aggregate}</div>
                </td>
                <td className="instalment-total-aggregate">
                    <div className="form-control input-format-currency">{aggregates.instalment_total_aggregate}</div>
                </td>
            </tr>
        );

        for (let el of Array.from(this.rowContainer.querySelectorAll('.instalment-schedule-aggregates div.input-format-currency'))) {
            el.innerHTML = Format.formatCurrency(el.innerHTML);
        }
    }

    _validateParams(params, err) {
        let valid = true;
        let gtzErrm = 'musi być liczbą większa od zera';

        function isGreaterThenZero(value) {
            return Input.isNumber(value) && value > 0;
        }

        if (!isGreaterThenZero(params.instalmentNumber)) {
            err.push(`Pole [Liczba rat] ${gtzErrm}.`);
            valid = false;
        }

        if (!isGreaterThenZero(params.capitalNet)) {
            err.push(`Pole [Kapitał netto]  ${gtzErrm}.`);
            valid = false;
        }

        if (!isGreaterThenZero(params.capitalNet)) {
            err.push(`Pole [Kapitał brutto] ${gtzErrm}.`);
            valid = false;
        }
        return valid;
    }

    /**
     * getCustomMapping - function os used for alternative instalment schedules, not based on the document_type_attribute_mapping parameters,
     * ie. when we have to generate few schedules before the main one (like proposal schedule and initial schedule in other section).
     * It's used od course only for dynamically generates schedules
     * If schedule section document type attribute covers features-> mapping{} entry, it will be treated as custom mapping and aply as it.
     * Mapping has structure as {mapping_name: id_of_the_attribute (code of the item)}
     * todo: list of required mapping attributes
     */
    getCustomMapping() {
        for (let [k, v] of Object.entries(this.customMapping)) {
            this.mapping[k] = {id: v, item: Input.getByCode(v)};
        }
    }

    async getMapping() {
        if (this.customMapping) {
            return new Promise((resolve, reject) => {
                this.getCustomMapping();
                resolve(true);
            });
        }
        return new Promise((resolve, reject) => {
            ajaxCall({
                method: 'get',
                url: SCHEDULE_MAPPING_URL,
                data: {idDocument: this.idDocument}
            }).then(
                (data) => {
                    for (let [k, v] of Object.entries(data)) {
                        this.mapping[k] = v;
                        this.mapping[k].item = Input.getByCode(v.id);
                    }
                    return resolve(true);
                },
                (resp) => {
                    reject(resp.errmsg);
                }
            )
        })
    }

    _getMappingValue(key, default_value = null) {
        let mapping = this.mapping[key];

        if (!mapping) {
            return default_value;
        }

        if (key === 'instalmentInterestRate') {
            let result = {};
            result[_g.settings.MINUS_INFINITY_DATE] = (mapping.item ? Input.getValue(mapping.item, default_value) : mapping.value);
            return result;
        }
        return mapping.item ? Input.getValue(mapping.item, default_value) : mapping.value;
    }

    _getScheduleItemsIds() {
        throw new SystemException(`[${this.constructor.name}][_getScheduleItemsIds]: not implemented`);
    }

    _getScheduleTable() {
        return Array.from(this.rowContainer.querySelectorAll('tr:not(.instalment-schedule-aggregates)')).map(i => {
            let instalmentMaturityDate = i.querySelector('.instalment-maturity-date');
            let instalmentCapital = i.querySelector('.instalment-capital');
            let instalmentCommission = i.querySelector('.instalment-commission');
            let instalmentTotal = i.querySelector('.instalment-total');
            let instalmentInterest = i.querySelector('.instalment-interest');

            return {
                maturityDate: {
                    value: instalmentMaturityDate ? Input.getValue(instalmentMaturityDate) : null,
                    change_flag: instalmentMaturityDate ? instalmentMaturityDate.dataset["__meta__change_flag"] : 0
                },
                instalmentCapital: {
                    value: instalmentCapital ? parseFloat(Input.getValue(instalmentCapital)) : 0,
                    change_flag: instalmentCapital ? instalmentCapital.dataset["__meta__change_flag"] : 0
                },
                instalmentCommission: {
                    value: instalmentCommission ? parseFloat(Input.getValue(instalmentCommission)) : 0,
                    change_flag: instalmentCommission ? instalmentCommission.dataset["__meta__change_flag"] : 0
                },
                instalmentInterest: {
                    value: instalmentInterest ? parseFloat(Input.getValue(instalmentInterest)) : 0,
                    change_flag: instalmentInterest ? instalmentInterest.dataset["__meta__change_flag"] : 0
                },
                instalmentTotal: {
                    value: instalmentTotal ? parseFloat(Input.getValue(instalmentTotal)) : 0,
                    change_flag: instalmentTotal ? instalmentTotal.dataset["__meta__change_flag"] : 0
                }
            }
        });
    }

    _generate(opts, mode) {
        // $(".loader-container").fadeIn();
        opts.scheduleTableData = this._getScheduleTable();

        this.cleanErrors();

        ajaxCall(
            {
                method: 'get',
                dataType: 'JSON',
                contentType: 'application/json',
                url: this.instalmentScheduleUrl,
                data: {opts: JSON.stringify(opts), mode: mode}
            },
            (res) => {
                if (!Array.isArray(res.sections)) {
                    jsUtils.LogUtils.log(`[${className}][generate]: Schedule response sections is not an array object: ${res}`);
                    return;
                }

                this._renderScheduleSections(res.sections);

                if (res.aggregates) {
                    this._renderAggregates(res.aggregates);
                }

                this.rowContainer.dispatchEvent(
                    new CustomEvent(
                        this.events.scheduleCreated,
                        {
                            detail: {
                                instalmentSchedule: this
                            },
                            bubbles: true
                        }
                    ));

                this.rowContainer.dispatchEvent(window.evtChanged);

            },
            (resp) => {
                console.error(resp);
                if (resp?.responseJSON?.errmsg) {
                    this.displayErrors(resp.responseJSON.errmsg);
                } else {
                    throw new Error(resp.responseText);
                }
            },
            () => {
                // $(".loader-container").fadeOut();
            });
    }

    generate(ask = false, reset = false) {
        let params;

        if (!this.opts) {
            let opts = {};
            for (let key of Object.keys(this.scheduleParamsDefaults)) {
                opts[key] = this._getMappingValue(key);
            }
            params = Object.assign({}, this.scheduleParamsDefaults, opts);

        } else {
            if (typeof this.instalmentInterestRateCallback === 'function') {
                try {
                    this.opts.instalmentInterestRate = this.instalmentInterestRateCallback();
                } catch (e) {
                    console.error(e);
                    return;
                }
            }
            params = this.opts;
        }

        params.documentId = this.idDocument;

        let err = [];
        if (!this._validateParams(params, err)) {
            this.displayErrors(`Brak wymaganych parametrów do wygenerowania harmonogramu: ${err}`);
            return;
        }

        if (ask) {
            Alert.questionWarning(
                'Czy na pewno wygenerować harmonogram?',
                'Wszystkie wprowadzone do harmonogramu zmiany zostaną utracone',
                () => {
                    if (reset) {
                        this.reset();
                    }
                    this._generate(params);
                });
        } else {
            if (reset) {
                this.reset();
            }
            this._generate(params);
        }
    }

    validateSchedule(el) {
        return new Promise((resolve, reject) => {
            let idx = this.getRowIdx(el);

            if (!Input.isNumber(idx)) {
                throw new SystemException(`[${className}][validateSchedule]: indeks elementu musi być liczbą. Proszę Zgłosić problem do administratora systemu`);
            }

            try {
                this.validator.validate(el);

            } catch (e) {
                Alert.warning(
                    'Błąd podczas walidacji harmonogramu', e.message +
                    `<br>Wprowadzona wartość: ${el.value} została anulowana i przywrócono wartość poprzednią:<br/>${el.dataset.current_value}. (lp: ${idx + 1})`);

                Input.setValue(el, el.dataset.current_value);
                reject();

                return false;
            }
            resolve();
            return true;
        });
    }

    /**
     * setMinDate - sets the minimum possible chooseable date for the next row maturity date
     * @param e - maturity date element being the source of minDate to the next row maturity date element
     * @param idx - index of the next row maturity date element
     */
    setMinDate(e, idx) {
        if (idx != null) {
            let prevDate = this.getRow(idx).querySelector(INSTALMENT_MATURITY_DATE_SELECTOR);
            let val = Input.getValue(prevDate);
            if (val) {
                e.minDate(new Date(val).addDays(1).defaultFormat());
            }
        }
    }

    _initSchedule() {
        if (!this.rowContainer) {
            return;
        }
        // set revert button when custom change entered to set item's default behaviour (if isn't disabled)
        for (let item of Array.from(
            this.rowContainer?.querySelectorAll('input[data-__meta__change_flag]:not([data-__meta__change_flag="0"])')
        )) {
            if (!item.disabled) {
                this._addRevertToDefaultBtn(item);
            }
        }

        // set last row readonly
        let tr = this.rowContainer.querySelector('tr:last-child');
        if (tr) {
            this._setLastRowReadOnly(tr);
        }

        this._getScheduleItemsIds();

        if (!this.opts) {
            // it means that instalment schedule is to be re-generated dynamically on change of the "global" external total values (like value, trotal commission etc.)
            //if opts are set the mapping is not needed.
            this.getMapping().then(() => {
                    this.validator = new InstalmentScheduleValidator(
                        this.rowContainer,
                        this.mapping?.capitalNet?.item,
                        this.mapping.commission ? this.mapping.commission.item : null,
                        this.mapping.startDate ? this.mapping.startDate.item : null
                    );

                    if (this.mapping.startDate?.item) {
                        this.mapping.startDate.item.addEventListener('change', () => {
                            this.generate(false, true);
                            this.mapping.startDate.item.dispatchEvent(window.evtChanged);
                        });
                    }

                    // add change event handlers for external fields.
                    // If any of below fields change, run instalment schedule generation
                    for (let i of [
                        //this.mapping.capitalNet.item,
                        this.mapping?.value?.item,
                        this.mapping?.instalmentNumber?.item,
                        this.mapping.instalmentCapital.item,
                        this.mapping?.instalmentCommission?.item,
                        this.mapping?.instalmentTotal?.item,
                        this.mapping.instalmentInterestRate.item,
                        this.mapping?.constantInstalment?.item,
                    ]) {
                        if (i) {
                            i.addEventListener('change', (e) => {
                                this.generate(false, true);
                                this.mapping.value.item.dispatchEvent(window.evtChanged);
                            });
                        }
                    }
                },
                (errmsg) => {
                    throw new SystemException(errmsg);
                });

        } else {
            this.validator = new InstalmentScheduleValidator(
                this.rowContainer,
                this.opts.capitalNet,
                this.opts.commission,
                this.opts.startDate,
                true
            );
        }
    }

    _addRevertToDefaultBtn(e) {
        /**
         * When a value of a schedule field has been changed, it's becoming an arbitrary field, what meant that entered value is
         * going to be taken explicitly - as it is. To set it back to default state the revert to default btn is added
         */

        // TODO: it needs to be subject for further thoughts. Turned off at the moment
        return;

        if (!e.parentElement.querySelector('.revert-to-default-btn')) {
            let revertBtn = ToolbarUtils.undoBtn();
            revertBtn.classList.add('revert-to-default-btn');
            e.parentElement.appendChild(revertBtn);
            revertBtn.addEventListener('click', () => {
                Alert.questionWarning(
                    'Czy na pewno zmienić wartość na domhyślną?',
                    'Harmonogram zostanie przeliczony ponownie. Inne wartości arbitralne zostaną zachowane.',
                    () => {
                        e.removeAttribute("data-__meta__change_flag");
                        revertBtn.remove();
                        this.generate();
                    }
                )
            })
        }
    }

    _handleChange(e) {
        if (Input.isNullValue(e.value)) {
            Input.setValue(e, e.dataset.current_value);
            Alert.error('Wartość nie może być pusta');
            return;
        }

        let idx = this.getRowIdx(e);
        let lastIdx = this.rowContainer.querySelectorAll("tr:not(.instalment-schedule-aggregates)").length - 1; // this.rowContainer.rows ? this.rowContainer.rows.length - 1 : 0;

        //check if schedule date has changed
        if (e.classList.contains(INSTALMENT_MATURITY_DATE_SELECTOR.substring(1)) || e.classList.contains('vanilla-date-field')) {
            // check either value is proper date or it raises exception
            let dt = new Date(Input.getValue(e));

            if (idx != null) {
                if (idx < lastIdx) {
                    Alert.questionWarning(
                        'Czy przeliczyć daty kolejnych rat?',
                        '',
                        () => {
                            let _idx = idx;

                            while (++_idx <= lastIdx) {
                                this.getRow(_idx).querySelector(INSTALMENT_MATURITY_DATE_SELECTOR).removeAttribute('data-__meta__change_flag');
                            }

                            e.dataset['__meta__change_flag'] = "2";
                            this._addRevertToDefaultBtn(e);
                            this.generate();
                        },
                        '',
                        () => {
                            this.validateSchedule(e).then(
                                () => {
                                    e.dataset['__meta__change_flag'] = "1";
                                    if (idx > 0) { // setting new minDate for schedule date
                                        this.setMinDate(e, idx - 1);
                                    }
                                    this._addRevertToDefaultBtn(e);
                                    this.generate();
                                }
                            )
                        });
                } else {
                    this.validateSchedule(e).then(
                        () => {
                            e.dataset['__meta__change_flag'] = "1";
                            if (idx > 0) { // setting new minDate for schedule date
                                this.setMinDate(e, idx - 1);
                            }
                            this._addRevertToDefaultBtn(e);
                            this.generate();
                        }
                    )
                }
            }

        } else {
            e.dataset['__meta__change_flag'] = "1";
            this._addRevertToDefaultBtn(e);
            this.generate();
        }
    };

    _calculateAggregatesInitial() {
        let capital = 0;
        let interest = 0;
        let total = 0;
        for (let i of Array.from(this.rowContainer.querySelectorAll('tbody tr'))) {
            capital += parseFloat(Input.getValue(i.querySelector('.instalment-capital')));
            interest += parseFloat(Input.getValue(i.querySelector('.instalment-interest')));
            total += parseFloat(Input.getValue(i.querySelector('.instalment-total')));
        }

        this._renderAggregates(
            {
                'instalment_capital_aggregate': capital,
                'instalment_interest_aggregate': interest,
                'instalment_total_aggregate': total
            }
        )
    }

    init() {
        if (_g?.document?.mode === 'DEFINITION') {
            return;
        }

        document.addEventListener('documentAttributeEvt:afterAttributesRender', () => {
            this._initSchedule();
            this._calculateAggregatesInitial();
        });

        // handling internal changes (schedule row items change)
        this.rowContainer.addEventListener('change', e => {
            this._handleChange(e.target);
        });

        // handling internal changes (schedule row items change)
        this.rowContainer.addEventListener('changeDate', e => {
            this._handleChange(e.target);
        });

        // handling internal changes (schedule row items change)
        $(this.rowContainer).on('dp.change', e => {
            this._handleChange(e.target);
        });
    }
}

export {
    InstalmentSchedule, INSTALMENT_CAPITAL_SELECTOR,
    INSTALMENT_MATURITY_DATE_SELECTOR,
    INSTALMENT_COMMISSION_SELECTOR,
    INSTALMENT_INTEREST_SELECTOR,
    INSTALMENT_TOTAL_SELECTOR
};
