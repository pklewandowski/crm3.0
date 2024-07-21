class Report {
    constructor(reportModalId) {
        this.templateCode = null;
        this.modalId = reportModalId;
        this.modal = document.getElementById(reportModalId);
        this.reportPreview = this.modal.querySelector('.report-preview');
        this.reportParams = this.modal.querySelector('.report-params');
        this.previewBtn = document.getElementById('previewReportBtn');
        this.generateBtn = document.getElementById('generateReportBtn');

        this.init();
    }

    _resetModal() {
        this.reportPreview.innerHTML = null;
        this.reportParams.innerHTML = null;
    }

    get(templateId) {
        ajaxCall(
            {
                method: 'get',
                url: '/report/api/template/',
                data: {templateId: templateId, documentId: _g.document.id}
            },
            (resp) => {
                this.templateCode = resp.code;
                // let iframe = $(modal).find('.report-preview-iframe'));
                // i.src='data:text/html;charset=utf-8,' + ;
                this._resetModal();

                let table = jsUtils.Utils.domElement('table', null, ['table', 'table-hover', 'table-striped', 'table-condensed', 'report-params-table']);
                table.style.tableLayout = 'fixed';

                let th = jsUtils.Utils.domElement('thead');
                th.innerHTML = "<tr><th>Nazwa</th><th>Wartość</th></tr>";
                table.appendChild(th);

                let tbody = jsUtils.Utils.domElement('tbody');
                table.appendChild(tbody);

                this.reportParams.appendChild(table);

                for (let [key, i] of Object.entries(resp.params)) {
                    let tr = jsUtils.Utils.domElement('tr');
                    tbody.appendChild(tr);
                    if (!Array.isArray(i)) {
                        let td = jsUtils.Utils.domElement('td');
                        td.innerText = i.name;
                        tr.appendChild(td);

                        td = jsUtils.Utils.domElement('td');
                        td.innerText = i.value;
                        tr.appendChild(td);
                    }
                }
                $(this.modal).modal();
            },
            (resp) => {
                Alert.error('Błąd', resp.responseJSON.errmsg);
                jsUtils.LogUtils.log(resp.responseJSON);
            }
        );
    }

    generate(preview = false) {
        if (!this.templateCode) {
            window.Alert.error('Kod szablonu raportu nie może być pusty!');
            return;
        }

        $(".loader-container").fadeIn();
        ajaxCall(
            {
                method: 'post',
                url: '/report/api/',
                data: {
                    'documentId': _g.document.id,
                    'templateCode': this.templateCode,
                    'preview': preview ? 'T' : ''
                }
            },
            (resp) => {
                if (preview) {
                    this.reportPreview.innerHTML = `<embed src="/media/reports/temp/${resp.reportName}" frameBorder="0" scrolling="auto" width="100%" type="application/pdf"/>`;
                } else {
                    window.location.reload()
                }
            },
            (resp) => {
                console.error(resp.responseJSON);
                window.Alert.error(resp.responseJSON.errmsg);
            },
            () => {
                $(".loader-container").fadeOut();
            });

    }

    init() {
        this.previewBtn.addEventListener('click', (e) => {
            this.generate(true);
        });
        this.generateBtn.addEventListener('click', (e) => {
            Alert.question('Czy na pewno wygenerować pismo?', '', ()=>{this.generate()});
        });
    }
}

export default Report;