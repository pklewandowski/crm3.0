import ajaxCall from "../../../../_core/ajax";
import {Format} from "../../../../_core/format/format";

class CashFlow {

    constructor(productId, container, formTemplate) {
        this.productId = productId;
        this.container = container || document.querySelector('#product-cashflow-formset-table tbody');
        ;
        this.formTemplate = formTemplate ||

            this.init();
    }

    getData() {
        let _this = this;
        ajaxCall({
                method: 'get',
                url: _g.product.urls.cashFlowUrl,
                data: {productId: _this.productId}
            },
            (resp) => {
                _this.data = resp;
                console.log(resp);
            },
            (resp) => {
                console.log(resp.responseJSON)
            }
        )
    }

    static getAggregates(productId, container, renderCallback = null, render = true) {
        ajaxCall({
                method: 'get',
                url: _g.product.urls.cashFlowAggregatesUrl,
                data: {productId: productId}
            },
            (resp) => {
            console.log(resp);
                if (render) {
                    if (typeof renderCallback === "function") {
                        renderCallback(resp);
                    } else {
                        CashFlow.renderAggregates(resp, container);
                    }
                } else {
                    return resp;
                }
            },
            (resp) => {
                console.error(resp.responseJSON);
                Alert.error('Błąd', resp.responseJSON.errmsg);
            }
        )
    }

    render(container, template) {
        if (!this.data) {
            return;
        }
    }

    static renderAggregates(resp, container) {
        let tbl = jsUtils.Utils.domElement('table', '', ['table', 'table-hover', 'table-bordered']);
        tbl.innerHTML = '<thead><tr><th>Typ przepływu</th><th>Rodaj przepływu</th><th>Suma</th></tr></thead>';
        let tb = jsUtils.Utils.domElement('tbody');
        tbl.appendChild(tb);
        for (let i of resp) {
            let tr = jsUtils.Utils.domElement('tr');
            tr.innerHTML =
                `<td class="cashflow-aggregates-type">${i.type}</td>
                 <td class="cashflow-aggregates-subtype">${i.subtype ? i.subtype : ''}</td>
                 <td class="cashflow-aggregates-sum">${Format.formatNumber(i.sum)}</td>`;
            tb.appendChild(tr);
        }
        container.appendChild(tbl);
    }

    init() {
    }
}

export default CashFlow;