import {HtmlTags} from "../../../../../../_core/htmlTags/html-tags";

class SectionTable {
    constructor(section) {
        this.section = section;
        this.headerColumns = this._getHeaderColumns();
        this.item = this._render();
    }

    _getHeaderColumns() {
        // get column names for header
        let headerColumns = [];
        if (this.section.at.children) {
            if (this.section.at?.feature?.rowNumbering) {
                let lp = HtmlTags.th(null, 'Lp.');
                lp.style.width = "5%";
                headerColumns.push(lp);
            }
            this.section.at.children.map(e => {
                if (e.is_column) {
                    headerColumns.push(HtmlTags.th(e, e.name));
                }
            });
            if (!this.section.readonly) {
                let th = document.createElement('th');
                th.innerText = 'Akcje';
                th.classList.add('repeatable-table-section-action-container');
                headerColumns.push(th);
            }
        }
        return headerColumns;
    }

    _render() {
        let table = jsUtils.Utils.domElement('table', '', ["table", "table-hover", "table-striped", "repeatable-section-tabs"]);
        table.style.tableLayout = 'fixed';
        let thead = jsUtils.Utils.domElement('thead');
        let theadTr = jsUtils.Utils.domElement('tr');
        thead.appendChild(theadTr);
        table.appendChild(thead);
        table.appendChild(this.section.rowContainer);

        this.headerColumns.map(e => {
            theadTr.appendChild(e);
        });

        return table;
    }
}

export {SectionTable};