import dateFormat from "dateformat";
import ajaxCall from "../../_core/ajax";
import {TabulatorTableUtils} from "./financePack/tabulatorTable/tabulator-table-utils";
import {ProductInstalmentSchedule} from "./financePack/schedule/product-instalment-schedule";
import CashFlow from "./financePack/cashFlow/cash-flow";
import {
    INSTALMENT_CAPITAL_SELECTOR,
    INSTALMENT_COMMISSION_SELECTOR,
    INSTALMENT_MATURITY_DATE_SELECTOR,
    INSTALMENT_TOTAL_SELECTOR
} from "./financePack/schedule/instalment-schedule";

import {Datepicker} from "../../_core/controls/vanillajs-datepicker-3ws";
import pl from "../../_core/controls/vanillajs-datepicker-3ws/js/i18n/locales/pl";
import "../../_core/controls/vanillajs-datepicker-3ws/dist/css/datepicker-bulma.css";
import {ProductDashboard} from "./financePack/dashboard/js/product-dashboard";
import {Product} from "./product";
import {calculateProductAggregates} from "./financePack/calculation/calculation";
import Alert from "../../_core/alert";
import Report from "../../report/js/report";

window.report = new Report('reportModal');

pl.pl.daysMin = ["Nd", "Pn", "Wt", "Śr", "Cz", "Pt", "So"];
Object.assign(Datepicker.locales, pl);

// formatters for tabulator table used for calculation rows displaying
TabulatorTableUtils.setFormatters();

function setDecimalField(el) {
    Input.setMask(el, 'currency');
}

let calcTable = null;
let calcHeader = null;
let calcData = null;


function deleteFormsetRow(e, msg, callback = null) {
    let that = e;
    Alert.questionWarning(
        'Czy na pewno usunąć wpis?',
        '',
        () => {
            that.parents('td').find('input').val('on');
            that.parents('tr').css('display', 'none');
        });
}

function setFormset(formsetTableId, formManagementId) {
    let totalCtrl = $(`#${formManagementId}`);
    let total = parseInt(totalCtrl.val());
    let formset = $(`#${formsetTableId} tr[data-status="new"]`);
    $.each(formset, function (i, e) {
        $.each($(e).find('input, select, textarea'), function (i1, e1) {
            e = $(e1);
            e.prop('name', e.prop('name').replace(/__prefix__/g, total));
        });
        total++;
    });
    totalCtrl.val(total);
    return total;
}

function createDataTable(scrollHeight) {
    $("#calculate_table").DataTable(
        {
            // destroy: true,
            // scrollY: scrollHeight,
            scrollY: 400,
            scrollX: true,
            scrollCollapse: true,
            searchBox: false,
            // "bLengthChange": false,
            // "bFilter": true,
            // "bInfo": false,
            // paging:         false,
            columnDefs: [
                {width: "100px", targets: 0, sorting: false}
            ],
            fixedColumns: {
                leftColumns: 1,
                rightColumns: 1
            }
        });
}

function resizePage() {
    const container = $("#calculate_table");
    const height = container.height() - container.find(".dataTables_scrollHead").height();
    updateDataTable(height + "px");
}

function updateDataTable(scrollHeight) {
    createDataTable(scrollHeight);
}

function setPreviousValue() {
    for (let i of Array.from(document.querySelectorAll(INSTALMENT_MATURITY_DATE_SELECTOR))) {
        i.dataset.current_value = Input.getValue(i);
    }

    for (let i of Array.from(document.querySelectorAll(INSTALMENT_CAPITAL_SELECTOR))) {
        i.dataset.current_value = Input.getValue(i);
    }

    for (let i of Array.from(document.querySelectorAll(INSTALMENT_COMMISSION_SELECTOR))) {
        i.dataset.current_value = Input.getValue(i);
    }

    for (let i of Array.from(document.querySelectorAll(INSTALMENT_TOTAL_SELECTOR))) {
        i.dataset.current_value = Input.getValue(i);
    }
}

function rowFormatter(row) {
    let interestColumns = [
        // 'interest_required',
        'interest_rate',
        'interest_daily',
        'interest_per_day',
        'interest_cumulated_per_day',
        //'is_interest_for_delay'
    ]
    let data = row.getData(); //get data object for row
    if (data.commission_required_from_schedule !== "0.00" || data.capital_required_from_schedule !== "0.00") {
        row.getElement().classList.add('calc-table-due-date');
    }

    if (data.interest_type === 'FOR_DELAY') {
        for (let column of interestColumns) {
            row.getCell(row.getTable().getColumn(column)).getElement().classList.add('calc-table-interest-delay')
        }
    } else if (data.interest_type === 'FOR_DELAY_MAX') {
        for (let column of interestColumns) {
            row.getCell(row.getTable().getColumn(column)).getElement().classList.add('calc-table-interest-delay-max')
        }
    }
}

function setCashFlowSubtype(subtype) {
    let options = typeof subtype === 'string' ? JSON.parse(subtype.replace(/'/g, '"')) : [{XX: 'ogólne'}];
    let out = '<select class="form-control input-md">__OPTIONS__</select>';
    let opt = '';
    for (let i of options) {
        let _opt = Object.entries(i);
        console.log(_opt);
        opt = opt + `<option value="${_opt[0][0]}">${_opt[0][1]}</option>`;
    }
    return out.replace('__OPTIONS__', opt)
}


$(document).ready(() => {
    setPreviousValue();

    for (let el of Array.from(document.querySelectorAll(".decimal-field input"))) {
        setDecimalField(el);
    }

    // when cell on calculation table is clicked, the details dialog appears
    $("#calcTab").on('shown.bs.tab', () => {
        if (!calcTable) {
            $("#calc-tab .loader-container").fadeIn(200);
            ajaxCall(
                {
                    method: 'get',
                    url: '/product/calc-table/',
                    data: {productId: _g.product.id}
                },
                (resp) => {
                    calcHeader = resp.header;
                    calcData = resp.data;
                    calcHeader[0].headerMenu = TabulatorTableUtils.headerMenu;
                    calcTable = TabulatorTableUtils.setTabulatorTable(
                        "#calculation-table", calcHeader, calcData, rowFormatter
                    );

                },
                (resp) => {
                    console.log('error');
                    console.log(resp);
                    Alert.error('Wystąpił wyjątek!', resp.responseJSON.errmsg);

                },
                () => {
                    $("#calc-tab .loader-container").fadeOut();
                }
            );

        } else {
            calcTable.redraw(true);
        }
    });

    $(document).on('click', "#product-cashflow-formset-container .add", function () {
        let form_idx = $('table#product-cashflow-formset-table tbody tr').length;
        let row = $("#cashflow-formset-row-template").html();
        let kstRow = $("#cashflow-formset-row-template-kst").html();
        let otherRow = $("#cashflow-formset-row-template-other").html();

        row = row.replace(/__PRODUCT_ID__/g, $(this).data('product_id'));
        row = row.replace("__ACCOUNTING_TYPE_ID__", $(this).data('accounting_type_id'));
        row = row.replace("__ACCOUNTING_TYPE_CODE__", $(this).data('accounting_type_code'));
        row = row.replace("__ACCOUNTING_TYPE_NAME__", $(this).data('accounting_type_name'));
        row = row.replace('__ACCOUNTING_DATE__', $(this).data('accounting_type_code') === 'cost' ? kstRow : otherRow);

        row = row.replace(/__prefix__/g, form_idx);
        $('#id_product-cashflow-TOTAL_FORMS').val(form_idx + 1);
        $("#product-cashflow-formset-table tbody").append(row);

        row = ($("#product-cashflow-formset-table tbody tr:last"));

        if ($(this).data('accounting_type_code') === 'cost') {
            row.find(".cashflow-subtype").html(setCashFlowSubtype($(this).data('subtypes')));
        }

        row.find("td.cashflow-accounting-type-name input").val($(this).data('accounting_type_id'));

        row.find(".vanilla-date-field").each(function (i, el) {
            // todo: bypass until date-calendar will be unified in whole project to vanillajs-calendar-3ws control
            el.datepicker = new Datepicker(el, {
                autohide: true,
                showOnClick: true,
                language: 'pl',
                format: 'yyyy-mm-dd'
            });
            // setDatePicker($(this));
        });

        //TODO: temporary switched off untill new form from jsUtils implemented
        // row.find(".decimal-field input").each(function (i, el) {
        //     setDecimalField(el);
        // });
    });

    $(document).on('click', "#product-tranche-formset-container .add", function () {
        let form_idx = $('table#product-tranche-formset-table tbody tr').length;
        let row = $("#tranche-formset-row-template").html();


        row = row.replace(/__PRODUCT_ID__/g, $(this).data('product_id'));
        row = row.replace(/__prefix__/g, form_idx);

        $('#id_product-tranche-TOTAL_FORMS').val(form_idx + 1);
        $("#product-tranche-formset-table tbody").append(row);

        row = ($("#product-tranche-formset-table tbody tr:last"));

        row.find(".vanilla-date-field").each(function (i, el) {
            // todo: bypass until date-calendar will be unified in whole project to vanillajs-calendar-3ws control
            el.datepicker = new Datepicker(el, {
                autohide: true,
                showOnClick: true,
                language: 'pl',
                format: 'yyyy-mm-dd'
            });
            // setDatePicker($(this));
        });

        //TODO: temporary switched off untill new form from jsUtils implemented
        // row.find(".decimal-field input").each(function (i, el) {
        //     setDecimalField(el);
        // });
    });

    document.querySelector('#product-cashflow-formset-container .reload-mt940').addEventListener('click', (e) => {
        Alert.questionWarning(
            'Czy na pewno załadować transakcje z plików MT940?',
            '',
            () => {
                ajaxCall({

                        method: 'put',
                        url: _g.product.urls.cashFlowUrl,
                        data: {id: e.target.dataset['product_id']}
                    },
                    () => {
                        window.location.reload();
                    },
                    (error) => {
                        jsUtils.LogUtils.log(error.responseJSON);
                        throw error;
                    });
            });
    });


    function deleteProduct(productId) {
        function deleteProductCallback(opts) {
            ajaxCall(
                {
                    method: 'delete',
                    url: '/product/api/',
                    data: {productId: opts.productId, reason: opts.reason}
                },
                (resp) => {
                    window.location = document.getElementById('showDocBtn').href;
                },
                (resp) => {
                    Alert.error('Błąd', resp.responseJSON.errmsg);
                }
            ).then();
        }

        Alert.questionWarning(
            'Czy na pewno usunąć produkt?',
            'Usunięcie produktu spowoduje utratę wszystkich wpisów (jak np. przepływy) i powrót do edycji produktu',
            () => {
                Alert.questionWarning('Jesteś pewien, że chcesz usunąć produkt?', '',
                    () => {
                        Alert.questionWarningInput('Podaj powód usunięcia', '',
                            deleteProductCallback, {productId: productId, reason: null});
                    });
            })
    }

    document.getElementById('removeProductBtn').addEventListener('click', () => {
        deleteProduct(_g.product.id)
    });

    $(document).on('click', "#product-interest-formset-container a.add", function () {
        let row = $("#interest-formset-row-template").html().replace(/__PRODUCT_ID__/g, $(this).data('product-id'));
        $("#product-interest-formset-table tbody").append(row);

        let dateField = $('#product-interest-formset-table tbody tr:last').find('.vanilla-date-field')[0];
        // todo: bypass until date-calendar will be unified in whole project to vanillajs-calendar-3ws control

        new Datepicker(dateField, {
            autohide: true,
            showOnClick: true,
            language: 'pl',
            format: 'yyyy-mm-dd'
        });
        // setDatePicker(dateField);
        Input.setValue(dateField, dateFormat(new Date(), 'yyyy-mm-dd'));
        // dateField.data('DateTimePicker').date(moment(new Date()).format('YYYY-MM-DD'));


        $('#product-interest-formset-table tbody tr:last').find('.decimal-field input').each(function (i, el) {
            setDecimalField(el);
        });
    });

    $(document).on('click', '.print-daycalc-btn', function (e) {
        let el = e.target;
        let calcDate = el.closest('#calcTableRowDetails').querySelector('table').dataset['calc_date'];

        ajaxCall({
                method: 'post',
                url: '/report/api/',
                data: {
                    documentId: _g.product.document.id,
                    templateCode: 'LOAN_STATE',
                    queryParams: `{"calc_date": "${calcDate}", "product_id":"${_g.product.id}"}`
                }
            },
            (res) => {
                window.core.downloadReport(res.reportId);
            },
            (res) => {
                console.error(res.responseJSON);
                window.Alert.error(res.responseJSON.errmsg);
            }
        )
    });

    let cashFlowAggregatesBtn = document.querySelector('.cashflow-aggregates-btn');
    let cashFlowAggregatesModal = document.getElementById('cashFlowAggregatesModal');

    cashFlowAggregatesBtn.addEventListener('click', (e) => {
        let container = document.querySelector('.cashflow-aggregates-container');
        if (!container.innerHTML.length) {
            CashFlow.getAggregates(_g.product.id, container);
        }
        $(cashFlowAggregatesModal).modal();
    });

    $('.btn-save').click(function () {
        setFormset('product-interest-formset-table', 'id_product-interest-TOTAL_FORMS');
        setFormset('product-cashflow-formset-table', 'id_product-cashflow-TOTAL_FORMS');
        setFormset('product-tranche-formset-table', 'id_product-tranche-TOTAL_FORMS');

        $("#loaderContainer").fadeIn();
        $('form#product-form').submit();
    });

    $(document).on('click', '#product-cashflow-formset-table > tbody > tr a.delete', function () {
        deleteFormsetRow($(this), 'Tak, usuń z listy!');
    });

    $(document).on('click', '#product-interest-formset-table > tbody > tr a.delete', function () {
        deleteFormsetRow($(this), 'Tak, usuń z listy!');
    });

    $(document).on('click', '#product-tranche-formset-table > tbody > tr a.delete', function () {
        deleteFormsetRow($(this), 'Tak, usuń z listy!');
    });

    $("#toggleInstalment, #toggleCost").change(function () {
        let showInstalment = $("#toggleInstalment").is(":checked");
        let showCost = $("#toggleCost").is(":checked");

        let instalmentRows = $(`#product-cashflow-formset-table tr[data-accounting_type="2"]`);
        let costRows = $(`#product-cashflow-formset-table tr[data-accounting_type="1"]`);

        if (showInstalment) {
            instalmentRows.show();
        } else {
            instalmentRows.hide();
        }
        if (showCost) {
            costRows.show();
        } else {
            costRows.hide();
        }
    });

    // let opts = {
    //     startDate: _g.product.startDate,
    //     capitalNet: _g.product.capitalNet,
    //     value: _g.product.value,
    //     commission: _g.product.commission,
    //     instalmentNumber: _g.product.instalmentNumber,
    //     instalmentCapital: _g.product.instalmentCapital,
    //     instalmentCommission: _g.product.instalmentCommission,
    //     instalmentInterestRate: null,
    //     instalmentInterestCapitalTypeCalcSource: _g.product.instalmentInterestCapitalTypeCalcSource
    // };
    //
    // let productInstalmentSchedule = new ProductInstalmentSchedule(
    //     document.getElementById('instalment-schedule-row-container'),
    //     _g.product.document.id,
    //     null,
    //     opts
    // );

// todo: bypass until date-calendar will be unified in whole project to vanillajs-calendar-3ws control
    for (let el of Array.from(document.querySelectorAll('.vanilla-date-field'))) {
        el.datepicker = new Datepicker(el, {
            autohide: true,
            showOnClick: true,
            language: 'pl',
            format: 'yyyy-mm-dd'
        });
        // workaround until unify calendar control: one for all items. Now we have two different calendars and need to move scheduler.schedule
        // to vanillajs-datepicker-3ws calendar
        el.minDate = function (minDate) {
            el.datepicker.setOptions({minDate: minDate});
        };
        el.addEventListener('changeDate', () => {
            el.dispatchEvent(new Event('change', {bubbles: true}));
        });
    }

    let product = new Product(_g.product.id);
    let productDashboard;

    product.getData().then(() => {
        if (product.data?.calculation_last && typeof product.data.calculation_last == 'object') {
            let dashboardData = Object.assign(product.data.calculation_last, calculateProductAggregates(product));

            productDashboard = new ProductDashboard(
                product.id,
                'productDashboardContainer',
                'productDashboardTemplate',
                dashboardData
            );
            productDashboard.bindData();
        }
    });

    let productInstalmentSchedule = new ProductInstalmentSchedule(
        document.getElementById('productInstalmentScheduleContainer'),
        _g.product.document.id,
        null,
        {
            'idProduct': _g.product.id,
            'value': _g.product.value,
            'capitalNet': _g.product.capitalNet,
            'instalmentInterestRate': _g.product.instalmentInterestRate,
            'instalmentInterestCapitalTypeCalcSource': _g.product.instalmentInterestCapitalTypeCalcSource,
            // 'instalmentTotal': 90000, //_g.product.total,
            'constantInstalment': 'T',
            'instalmentNumber': _g.product.instalmentNumber
            // 'startDate': _g.product.startDate
        }
    )

    let btn = productInstalmentSchedule.toolbar.addButton(
        null,
        '',
        'fa fa-redo',
        'Generuj harmonogram',
        () => {
            productInstalmentSchedule.generate();
        },
        null);

    btn.style = "margin-right: 5px; float: right; cursor: pointer;"

    // document.querySelector('.btn-print-balance').addEventListener('click', e => {
    //     report.get(null, 'BALANCE_PER_DAY', _g.product.document.id)
    // });

    let productForm = new formUtils.Form(
        document.getElementById('productFormContainer'),
        document.getElementById('productFormTemplate'),
        null,
        null,
        {'reloadOnSave': true}
    );

    document.getElementById('productEditBtn').addEventListener('click', e => {
        productForm.getData(_g.product.id);
        productForm.show();
    });


    let temp = document.getElementById('capitalizationDate');
    temp.datepicker = new Datepicker(temp, {
        autohide: true,
        showOnClick: true,
        language: 'pl',
        format: 'yyyy-mm-dd'
    });

    document.getElementById('productStatuses').addEventListener('click', e => {
        Alert.questionWarning('Czy na pewno zmienić status produktu?', '', () => {
            ajaxCall({
                    method: 'put',
                    url: "/product/api/product-status/",
                    data: {"id": _g.product.id, "status": e.target.value}

                },
                (resp) => {
                    console.log(resp)
                    window.location.reload();
                },
                (resp) => {
                    jsUtils.LogUtils.log(resp.responseJSON)
                    Alert.error(null, resp.responseJSON.errmsg, null, null, resp.responseJSON.errtype)
                }
            );
        });
    });

    document.getElementById('revertProductStatus').addEventListener('click', e => {
        Alert.questionWarning(
        'Czy na pewno cofnąć status?',
        '',
        () => {
            ajaxCall(
                {
                    method: 'patch',
                    url: "/product/api/product-status/",
                    data: {"id": _g.product.id}
                },
                () => {
                    window.location.reload();
                },
                (resp) => {
                    let res = resp.responseJSON;
                    Alert.error('Błąd', res.errmsg);
                });
        });
    })
});
