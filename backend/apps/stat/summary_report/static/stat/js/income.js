const Income = function (incomeContainer) {
    this.container = incomeContainer;
    let _this = this;
    let contentTableHeader = $("#incomeContentTableHeaderTemplate").html();
    let contentTableRow = $("#incomeContentTableRowTemplate").html();
    let contentTableSumRow = $("#incomeContentTableSumRowTemplate").html();
    let incomeMcTabHeader = $("#incomeMcTabHeaderTemplate").html();
    let incomeMcTabContent = $("#incomeMcTabContentTemplate").html();


    function _renderIncomeMcTabHeader(data) {
        let tabs = '<ul class="nav nav-tabs">';
        $.each(data, function (i, e) {
            tabs += incomeMcTabHeader.replace(/__TAB_ID__/g, e).replace('__ACTIVE__', i === 0 ? 'active' : '');
        });
        tabs += '</ul>';
        $("#incomeMcTabs").html(tabs);
    }

    function _renderIncomeRows(data) {
        let rows = '';

        let sumCount = 0;
        let sumAmountRequested = 0.0;
        let sumAmountAwared = 0.0;

        $.each(data, function (i1, e1) {
            let row = contentTableRow;
            let adviserName = e1.company_name ? e1.company_name : `${e1.last_name ? e1.last_name : ''} ${e1.first_name ? e1.first_name : ''}`;

            row = row.replace('__ADVISER_NAME__', adviserName !== ' ' ? adviserName : '-');
            row = row.replace('__COUNT__', e1.cnt);
            row = row.replace('__AMOUNT_REQUESTED__', e1.amount_requested ? formatCurrency(e1.amount_requested) : '-');
            row = row.replace('__AMOUNT_GRANTED__', e1.amount_granted ? formatCurrency(e1.amount_granted) : '-');
            row = row.replace('__COMMISSION__', '-');
            rows += row;

            sumCount += parseInt(e1.cnt);
            sumAmountRequested += e1.amount_requested ? parseFloat(e1.amount_requested) : 0.0;
            sumAmountAwared += e1.amount_granted ? parseFloat(e1.amount_granted) : 0.0
        });

        let row = contentTableSumRow;
        row = row.replace('__COUNT__', sumCount);
        row = row.replace('__AMOUNT_REQUESTED__', formatCurrency(sumAmountRequested));
        row = row.replace('__AMOUNT_GRANTED__', formatCurrency(sumAmountAwared));
        row = row.replace('__COMMISSION__', '-');

        rows += row;

        return rows;
    }

    // function _renderIncomeData(data) {
    //     let tbl = `<table class="table table-bordered">${contentTableHeader}<tbody>__TABLE_CONTENT__</tbody></table>`;
    //     let html = '';
    //
    //     $.each(data.mc, function (i, e) {
    //         let content = incomeMcTabContent.replace(/__TAB_ID__/g, e).replace('__ACTIVE__', i === 0 ? 'active' : '');
    //         let rows = _renderIncomeRows(data.data[e]);
    //         let contentTable = tbl.replace('__TABLE_CONTENT__', rows);
    //
    //         content = content.replace('__TAB_DATA__', contentTable);
    //         html += content;
    //     });
    //     _this.container.html(html);
    // }

    function _renderIncomeData(data) {
        if (!data) {
            return;
        }
        let tableHeader = '<tr><th></th>';
        let _tableHeader = '<tr><th>Doradca</th>';
        let tableContent = '';

        let tbl = `<table class="table table-bordered"><thead>__TABLE_HEADER__</thead><tbody>__TABLE_CONTENT__</tbody></table>`;
        let html = '';

        if (!(data.columns && data.columns.length)) {
            $("#incomeData").html(null);
            return;
        }

        for (let i = 1; i < data.columns.length; i++) {
            tableHeader += `<th colspan="4">${data.columns[i]}</th>`;
            _tableHeader += '<th>Kwota wnioskowana</th><th>Kwota przyznana</th><th>Prowizja</th><th>Liczba</th>';
        }

        tableHeader += `<th class="data-sum" colspan="4">${data.columns[0]}</th></tr>`;
        _tableHeader +=
            `<th  class="data-sum data-sum-total-v">Kwota wnioskowana</th>` +
            `<th class="data-sum">Kwota przyznana</th>` +
            `<th class="data-sum">Prowizja</th>` +
            `<th class="data-sum">Liczba</th></tr>`;

        tableHeader += _tableHeader;

        for (let i = 0; i < data.index.length; i++) {
            let classname = '';
            if (i === data.index.length - 1) {
                classname = 'data-sum data-sum-total';
            } else {
                classname = '';
            }
            tableContent += `<tr><td class="${classname}">${data.index[i]}</td>`;

            for (let j = 1; j < data.count[i].length; j++) {
                tableContent +=
                    `<td class="${classname}">${formatCurrency(data.sum_req[i][j], '-')}</td>` +
                    `<td class="${classname}">${formatCurrency(data.sum_gr[i][j], '-')}</td>` +
                    `<td class="${classname}">${formatCurrency(data.sum_cm[i][j], '-')}</td>` +
                    `<td class="${classname}">${data.count[i][j]}</td>`;
            }
            tableContent +=
                `<td class="data-sum data-sum-total-v ${classname}">${formatCurrency(data.sum_req[i][0], '-')}</td>` +
                `<td class="data-sum ${classname}">${formatCurrency(data.sum_gr[i][0], '-')}</td>` +
                `<td class="data-sum ${classname}">${formatCurrency(data.sum_cm[i][0], '-')}</td>` +
                `<td class="data-sum ${classname}">${data.count[i][0]}</td>`;
        }

        tbl = tbl.replace('__TABLE_HEADER__', tableHeader).replace('__TABLE_CONTENT__', tableContent);

        $("#incomeData").html(tbl);
    }


    this.renderData = function (data) {
        //_renderIncomeMcTabHeader(data.mc);
        _renderIncomeData(data);
    };

    this.collectData = function () {
        let data = $('form').serializeArray();
        data.push({name: 'csrfmiddlewaretoken', value: _g.csrfmiddlewaretoken, dataType: 'income'});
        $.ajax({
            url: _g.stat.urls.getDataUrl,
            method: 'post',
            data: data,
            success: function (resp) {
                _this.renderData(resp)
            }
        })
    }
};

export default Income;