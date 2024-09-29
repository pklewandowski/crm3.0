import {SystemException} from "../../../exception";
import {Paginator} from "../../paginator/js/paginator";

const className = 'Table';

class Table {
    constructor(container, dataUrl) {
        if (!container) {
            throw new SystemException(`[${className}] no container provided`);
        }
        this.container = container;
        this.paginatorContainer = null;

        this.header = null;
        this.data = [];
        this.paginator = new Paginator(this.paginatorContainer);

        this.dataUrl = dataUrl;
        this.currentPage = 1;
        this.pageCount = null;
    }



    getMetaData() {
        ajaxCall({
            method: 'get',
            url: this.dataUrl,
            data: {action: '__METADATA__'}
        }).then((metadata) => {
                this.paginator.container =
                this.header = metadata.header;
                this.pageCount = metadata.page_count;
            },
            (resp) => {
                throw new SystemException(resp);
            }
        );
    }

    getPage(pageNumber) {
        ajaxCall({
            method: 'get',
            url: this.dataUrl,
            data: {action: '__PAGE__'}
        }).then((data) => {
                this.data.push(data);
            },
            (resp) => {
                throw new SystemException(resp);
            }
        );

    }

    resetData() {
        this.data = [];
    }


    _renderHeader() {
        let thead = jsUtils.Utils.domElement('thead');
        let tr = jsUtils.Utils.domElement('tr');
        for (let column of this.header.columns) {
            let th = jsUtils.Utils.domElement('th');
            th.innerText = column.name;
            tr.appendChild(th);
        }
        thead.appendChild(tr);
        return thead;
    }

    _renderBody(data) {
        let tbody = jsUtils.Utils.domElement('tbody');
        for (let row of data) {
            let tr = jsUtils.Utils.domElement('tr');
            tr.appendChild(jsUtils.Utils.domElement('td', null, null, null, null, null, row.creation_date));
            tr.appendChild(jsUtils.Utils.domElement('td', null, null, null, null, null, row.text));

            tbody.appendChild(tr);
        }
        return tbody;
    }

    render(data) {
        this.reset();
        let table = jsUtils.Utils.domElement('table', null, ['table', 'table-hover']);
        table.appendChild(this._renderHeader());
        table.appendChild(this._renderBody(data));

        this.container.appendChild(table);
    }
}

export {Table};