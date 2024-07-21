import FormValidation from "../../../form/form-validaion";
import '../../../../csv/scss/csv.scss';

class FileUploadControl {
    constructor(container, dataTable, name, url, userType, mimeTypes = null, maxSizeMB = null) {
        this.container = container;
        this.dataTable = dataTable;
        this.dataContainer = this.container.querySelector('.csv-data-container');
        this.messagePanel = jsUtils.Utils.domElement('div', '', 'csv-message-panel');
        this.name = name;
        this.ctl = null;
        this.uploadBtn = null;
        this.initialUploadBtnText = 'Wybierz plik';
        this.url = url;
        this.userType = userType;
        this.mimeTypes = mimeTypes; // eg. ['image/jpeg', 'image/png', etc...]
        this.maxSizeMB = maxSizeMB;


        this.init();
    }

    _renderUploadBtn() {
        let uploadBtn = jsUtils.Utils.domElement('button', null, ['btn', 'btn-default']);
        uploadBtn.innerText = this.initialUploadBtnText;
        uploadBtn.addEventListener('click', () => {
            if (!this.ctl.files.length) {
                this.reset();
                this.ctl.click();
                return;
            }
            Alert.questionWarning('Czy na pewno wgrać dane?', '', () => {
                if (this.validate()) {
                    this.upload();
                }
            });
        });
        return uploadBtn;
    }

    _renderHeader(header) {
        if (!header) {
            return '';
        }

        let thead = jsUtils.Utils.domElement('thead');
        let tr = jsUtils.Utils.domElement('tr');
        let th = jsUtils.Utils.domElement('th');
        th.innerText = 'Nr wiersza';
        tr.appendChild(th);
        thead.appendChild(tr);

        for (let i of header) {
            th = jsUtils.Utils.domElement('th');
            th.innerText = i;
            tr.appendChild(th);
        }
        this.dataTable.appendChild(thead);
    }

    renderData(csvData) {
        if (!csvData) {
            return;
        }
        let header = csvData.header;
        let data = csvData.data;

        this.messagePanel.innerText = csvData.errmsg;

        this._renderHeader(header);
        let tbody = jsUtils.Utils.domElement('tbody');
        this.dataTable.appendChild(tbody);

        for (let i in data) {
            let row_error = false;
            let tr = jsUtils.Utils.domElement('tr');
            let td = jsUtils.Utils.domElement('td');

            td.innerText = data[i].__row__; //parseInt(i) + 1;
            tr.appendChild(td);

            //Check for row level errors
            if (data[i].__errors__.length) {
                let msg = [];

                for (let e of data[i].__errors__) {
                    if (e.field === '__row__') {
                        msg.push(e.message);
                    }
                }
                if (msg.length) {
                    tr.classList.add('error');
                    FormValidation.addErrors({'any': msg}, '', '', td);
                    row_error = true;
                }
            }

            for (let j of header) {
                if (j === '__errors__') {
                    continue;
                }

                td = jsUtils.Utils.domElement('td');
                td.innerText = data[i][j.toLowerCase()];

                //check for item level errors
                if (data[i].__errors__.length) {
                    for (let e of data[i].__errors__) {
                        if (e.field === j) {
                            FormValidation.addErrors({j: [e.message]}, '', '', td);
                        }
                    }
                }
                tr.appendChild(td);
            }
            tbody.appendChild(tr);
        }
    }

    renderErrors(errors) {
        if (!errors) {
            return;
        }
        this.dataTable.innerHTML = null;

        let html = '';

        for (let [idx, i] of Object.entries(errors)) {
            for (let err of i) {
                html += `<tr class="error"><td>[${idx}]: ${err.message} rekord: ${err.row}  ${err.missing ? "brakuje: " + err.missing : ''}</td>`;
            }
        }
        this.dataTable.innerHTML = html;
    }

    render() {
        let innerDiv = jsUtils.Utils.domElement('div');
        this.ctl = jsUtils.Utils.domElement('input', null, ['form-control', 'input-md']);
        this.ctl.type = 'file';
        this.ctl.style.display = 'none';

        this.uploadBtn = this._renderUploadBtn();
        this.ctl.addEventListener('change', () => {
            if (this.ctl.files.length) {
                this.uploadBtn.innerText = `Załaduj plik ${this.ctl.files[0].name}`;
            }
        });

        innerDiv.appendChild(this.ctl);
        innerDiv.appendChild(this.uploadBtn);

        this.container.appendChild(innerDiv);
        this.container.appendChild(this.messagePanel);
    }

    validate() {
        // user has not chosen any file
        if (this.ctl.files.length === 0) {
            alert('Error : No file selected');
            return false;
        }

        // first file that was chosen
        let file = this.ctl.files[0];

        // validate file type
        if (this.mimeTypes) {
            if (this.mimeTypes.indexOf(file.type) === -1) {
                jsUtils.LogUtils.log('Error : Incorrect file type');
                return false;
            }
        }

        // validate file size
        if (file.size > this.maxSizeMB * 1024 * 1024) {
            jsUtils.LogUtils.log('Error : Exceeded size');
            return false;
        }
        return true;
    };

    reset() {
        this.ctl.value = null;
        this.uploadBtn.innerText = this.initialUploadBtnText;
        this.dataTable.innerHTML = null;
        this.messagePanel.innerHTML = null;
    }

    upload() {
        let _this = this;
        let data = new FormData();

        // file selected by the user
        // in case of multiple files append each of them
        data.append('file', this.ctl.files[0]);
        data.append('csrfmiddlewaretoken', _g.csrfmiddlewaretoken);

        let request = new XMLHttpRequest();
        request.open('POST', this.url);

        // upload progress event
        request.upload.addEventListener('progress', function (e) {
            let percent_complete = (e.loaded / e.total) * 100;

            // percentage of upload completed
        });

        // AJAX request finished event
        request.addEventListener('load', function (e) {
            _this.reset();
            // HTTP status message
            if (request.status === 201) {
                let resp = JSON.parse(request.response);
                _this.messagePanel.innerHTML = `Dane zostały załadowane poprawnie. Możesz je przejrzeć klikając ten 
<a href="/${_this.userType}/list/${resp.processId}"><strong><u>link</u></strong></a>`;
                return;
            }
            if (request.status === 400) {
                _this.renderData(JSON.parse(request.response));
                return;
            }
            if (request.status === 422) {
                _this.renderErrors(JSON.parse(request.response));
                return;
            }

            _this.messagePanel.innerText = JSON.parse(request.response).errmsg;
        });

// send POST request to server side script
        request.send(data);
    }

    init() {
        this.render();
    }
}

export {FileUploadControl};