import ajaxCall from "../../../_core/ajax";
import Alert from "../../../_core/alert";

const INSTALMENT_OVERDUE_COUNT = 'INSTALMENT_OVERDUE_COUNT';
const EACH_INSTALMENT = 'EACH_INSTALMENT';
const EACH_OVERDUE_INSTALMENT = 'EACH_OVERDUE_INSTALMENT';

class Rules {
    constructor(actionRowContainer) {
        this.actionRowContainer = actionRowContainer;
        this.init();
    }

    static toggleSelectAccess(select, disabled = false, exclude = []) {
        for (let i of select.options) {
            if (disabled) {
                if (exclude.length && !exclude.includes(i)) {
                    i.setAttribute('disabled', 'disabled');
                }
            } else {
                i.removeAttribute('disabled');
            }
        }
    }

    static enableItem(item, enabled) {
        if (enabled) {
            item.removeAttribute('disabled');
            if (item.dataset['value']) {
                Input.setValue(item, item.dataset['value']);
            }
        } else {
            item.dataset['value'] = Input.getValue(item);
            Input.empty(item);
            item.setAttribute('disabled', 'disabled');
        }
    }

    sortActionList() {
        let list = this.actionRowContainer.querySelectorAll('tr');
        let idx = 1;
        for (let i of Array.from(list)) {
            i.querySelector('.rule-sq').value = idx++;
        }
    }

    // setFinancialRulesLayout(e) {
    //
    //     let tr = null;
    //
    //     if (e.target) {
    //         tr = e.target.closest('tr');
    //     } else {
    //         tr = e;
    //     }
    //
    //     let afterBefore = tr.querySelector('.rule-after-before');
    //     let what = tr.querySelector('.rule-what');
    //
    //     let days = tr.querySelector('.rule-days');
    //     let conditionalOperator = tr.querySelector('.rule-conditional-operator');
    //     let conditionalValue = tr.querySelector('.rule-conditional-value');
    //     let statusChangeFrom = tr.querySelector('.rule-status-change-from');
    //     let statusChangeTo = tr.querySelector('.rule-status-change-to');
    //
    //     let beforeOption = afterBefore.querySelector('option[value="BEFORE"]');
    //     let afterOption = afterBefore.querySelector('option[value="AFTER"]');
    //     let ifOption = afterBefore.querySelector('option[value="IF"]');
    //
    //     // Rule no 1.
    //     // when 'IF' condition is set, the only INSTALMENT_OVERDUE_COUNT option can be selected and 'days' set to null and disabled
    //     if (afterBefore.value === 'IF') {
    //         Rules.enableItem(days, false);
    //
    //         Input.setValue(what,  INSTALMENT_OVERDUE_COUNT);
    //         Rules.toggleSelectAccess(what, true, [tr.querySelector(`.rule-what option[value=${INSTALMENT_OVERDUE_COUNT}]`)]);
    //
    //     } else {
    //         Rules.enableItem(days, true);
    //         Rules.toggleSelectAccess(tr.querySelector('.rule-what'));
    //     }
    //
    //     // Rule no.2
    //     if (what.value === INSTALMENT_OVERDUE_COUNT) {
    //         beforeOption.setAttribute('disabled', 'disabled');
    //         afterOption.removeAttribute('disabled');
    //         ifOption.removeAttribute('disabled');
    //
    //         Rules.enableItem(conditionalOperator, true);
    //         Rules.enableItem(conditionalValue, true);
    //
    //         if (afterBefore.value === 'BEFORE') {
    //             afterBefore.value = 'AFTER';
    //         }
    //     } else if (what.value === EACH_INSTALMENT) {
    //         beforeOption.removeAttribute('disabled');
    //         afterOption.removeAttribute('disabled');
    //         ifOption.setAttribute('disabled', 'disabled');
    //
    //         Rules.enableItem(conditionalOperator, false);
    //         Rules.enableItem(conditionalValue, false);
    //
    //         if (Input.getValue(afterBefore) === 'IF') {
    //             Input.setValue(afterBefore, 'BEFORE');
    //         }
    //
    //     } else if (what.value === EACH_OVERDUE_INSTALMENT) {
    //         beforeOption.setAttribute('disabled', 'disabled');
    //         afterOption.removeAttribute('disabled');
    //         ifOption.setAttribute('disabled', 'disabled');
    //
    //         Rules.enableItem(conditionalOperator, false);
    //         Rules.enableItem(conditionalValue, false);
    //
    //         Input.setValue(afterBefore,'AFTER');
    //
    //     } else {
    //         beforeOption.removeAttribute('disabled');
    //         afterOption.removeAttribute('disabled');
    //         ifOption.setAttribute('disabled', 'disabled');
    //
    //         Rules.enableItem(conditionalOperator, false);
    //         Rules.enableItem(conditionalValue, false);
    //     }
    //
    //     // Rule no. 3
    //     if (Input.isNullValue(statusChangeFrom.value)) {
    //         statusChangeTo.length = 0;
    //     }
    //     if (e.target && e.target === statusChangeFrom) {
    //         ajaxCall(
    //             {
    //                 url: _g.document.type.urls.statusUrl,
    //                 method: 'get',
    //                 data: {status: statusChangeFrom.value, documentId: _g.document.type.id}
    //             },
    //             (resp) => {
    //                 console.log(resp);
    //                 statusChangeTo.length = 0;
    //                 for (let i of resp) {
    //                     statusChangeTo.appendChild(new Option(i[1], i[0]));
    //                 }
    //             },
    //             (resp) => {
    //                 console.error(resp.responseJSON);
    //             }
    //         )
    //     }
    // }

    setFinancialRulesLayout(e) {

        let tr = null;

        if (e.target) {
            tr = e.target.closest('tr');
        } else {
            tr = e;
        }

        let afterBefore = tr.querySelector('.rule-after-before');
        let what = tr.querySelector('.rule-what');
        let condition = tr.querySelector('.rule-condition');

        let days = tr.querySelector('.rule-days');
        let conditionalOperator = tr.querySelector('.rule-conditional-operator');
        let conditionalValue = tr.querySelector('.rule-conditional-value');
        let statusChangeFrom = tr.querySelector('.rule-status-change-from');
        let statusChangeTo = tr.querySelector('.rule-status-change-to');

        // Rule no. 1
        if (!Input.isNullValue(afterBefore.value)) {
            Rules.enableItem(days, true);
            Rules.enableItem(what, true);

        } else {
            Rules.enableItem(days, false);
            Rules.enableItem(what, false);
        }

        // Rule no. 2
        if (!Input.isNullValue(condition.value)) {
            Rules.enableItem(conditionalOperator, true);
            Rules.enableItem(conditionalValue, true);

        } else {
            Rules.enableItem(conditionalOperator, false);
            Rules.enableItem(conditionalValue, false);
        }

        // Rule no. 3
        if (Input.isNullValue(statusChangeFrom.value)) {
            statusChangeTo.length = 0;
        }

        if (e.target && e.target === statusChangeFrom) {
            ajaxCall(
                {
                    url: _g.product.type.urls.statusUrl,
                    method: 'get',
                    data: {status: statusChangeFrom.value, documentId: _g.document.type.id}
                },
                (resp) => {
                    console.log(resp);
                    statusChangeTo.length = 0;
                    for (let i of resp) {
                        statusChangeTo.appendChild(new Option(i[1], i[0]));
                    }
                },
                (resp) => {
                    console.error(resp.responseJSON);
                }
            )
        }
    }

    setMask(itemList) {
        for (let i of itemList) {
            Input.setIntegerMask(i, 0, 1000);
        }
    }

    _setActions() {
        this.actionRowContainer.addEventListener('click', (e) => {
            if (e.target.classList.contains('rule-toggle-btn')) {
                let actionListClicked = e.target.closest('td').querySelector('.rule-list-container');
                actionListClicked.style.display = 'block';
            }
        });

        this.actionRowContainer.addEventListener('change', (e) => {
            this.setFinancialRulesLayout(e);
        });

        this.actionRowContainer.addEventListener('click', (e) => {
            let el = e.target;
            if (el.classList.contains('rule-delete-btn')) {
                Alert.question('Czy na pewno usunąć regułę?', '', () => {
                    let tr = el.closest('tr');
                    tr.style.display = 'none';
                    tr.querySelector('.rule-delete-chk input').checked = true;
                })
            }
        });
    }

    init() {
        $('.rule-list tbody').sortable({
            handle: ".rule-list-sort-anchor i",
            stop: () => {
                this.sortActionList();
            }
        });

        this._setActions();

        for (let i of Array.from(this.actionRowContainer.querySelectorAll('tr'))) {
            this.setFinancialRulesLayout(i);
        }
        this.setMask(Array.from(this.actionRowContainer.querySelectorAll('tr .rule-days')));
        this.setMask(Array.from(this.actionRowContainer.querySelectorAll('tr .rule-conditional-value')));
        this.setMask(Array.from(this.actionRowContainer.querySelectorAll('tr .rule-time')));
    }
}

export default Rules;
