import Alert from "../../../../../../_core/alert";
import HtmlUtils from "../../../../../../_core/utils/html-utils";
import RepeatableSectionBase from "../repeatable-section-base";
import DocumentAttributeRenderer from "../../../../renderer/document-attribute-renderer";
import {TOOLBAR_BTN, ToolbarUtils} from "../../../../../../_core/utils/toolbar-utils";
import {Panel} from "./panel";

const className = 'RepeatableTableSection';

class RepeatableTableSection extends RepeatableSectionBase {

    constructor(at, renderCallback, level, ver = null) {
        super(at, renderCallback, level, ver);

        this.rowContainer = jsUtils.Utils.domElement('tbody', null, ['repeatable-section-tabs', 'row-container']);
        this.rowHeader = this.rowContainer;
        this.panel = new Panel(this);
        this.errorContainer = jsUtils.Utils.domElement('div', '', 'schedule-section-warning');
        this.errorContainer.style.display = 'none';

        this.panel.panelBody.appendChild(this.errorContainer);
        this.cl.appendChild(this.panel.item);

    }

    displayErrors(errMsg, reset = true) {
        if (reset) {
            this.reset();
        }
        this.errorContainer.innerText = errMsg;
        this.errorContainer.style.display = 'block';
    }

    cleanErrors() {
        this.errorContainer.style.display = 'none';
        this.errorContainer.innerText = null;
    }

    resetErrors() {
        this.errorContainer.innerHTML = null;
        this.errorContainer.style.display = 'none';
    }

    //todo: finally move to global js file related to render html objects
    static th(at, text) {
        let th = jsUtils.Utils.domElement('th');
        th.innerText = HtmlUtils.escapeScriptTag(text);
        if (at?.feature?.width) {
            th.style.width = at.feature.width;
        }
        return th;
    }

    getContainer() {
        return this.cl;
    }

    static addHeader(name, id, active) {
    }

    static addRowContainer(name, id, active) {
        let row = document.createElement('tr');
        row.id = id;
        row.classList.add(...['subsection', 'repeatable-section-tab', 'repeatable-section-tab-content', 'tab-pane']);
        row.dataset['href'] = id;

        return row;
    }

    get(idx) {
        return this.rowContainer.rows[idx];
    }

    getLast() {
        if(!this.rowContainer.rows.length) {
            return null;
        }
        return this.rowContainer.rows[this.rowContainer.rows.length - 1];
    }

    add(data, visible = true) {
        let idx = this.getTabLength();
        let row = RepeatableTableSection.addRowContainer(this.at.name, `${this.at.id}__${idx}__tab`);

        if (!_g.document.mode || _g.document.mode !== 'DEFINITION') {
            if (this.at.feature && this.at.feature.rowNumbering) {
                row.appendChild(jsUtils.Utils.domElement('td', null, null, null, null, (idx + 1).toString()));
            }
        }

        let predefined = null;

        if (this.at?.feature?.predefined &&
            data && data[this.at.feature.predefined.rowlabel]) {
            predefined = {
                label: data[this.at.feature.predefined.rowlabel][idx]?.value,
                field: this.at.feature.predefined.field,
                rowlabel: this.at.feature.predefined.rowlabel,
                rowid: this.at.feature.predefined.rowid
            }
        }

        this.renderCallback(this.at.children, data, row, idx, this.level + 1, predefined, null, this.ver);

        // ad action button container
        if (!this.readonly()) {
            let actionBtnContainer = document.createElement('td');
            row.appendChild(actionBtnContainer);

            let tbDelBtn = ToolbarUtils.deleteBtn(TOOLBAR_BTN.sm);
            tbDelBtn.style.position = 'relative';
            tbDelBtn.addEventListener('click', (e) => {
                RepeatableTableSection.delete(tbDelBtn);
            });
            actionBtnContainer.appendChild(tbDelBtn);
        }

        this.rowContainer.appendChild(row);
        DocumentAttributeRenderer.setCalculable(this.at.children, idx);
        return row;
    }

    /**
     * updateBySelector
     * Function updates data row according to selector specified with data dict.
     * Ie: {".instalment-maturity-date": "2021-01-01"} => Input.setValue(row.querySelector('.instalment-maturity-date'), "2021-01-01")
     * @param idx
     * @param data - dict covering row of data in form of fields selectors with values attached to. {field-selector: value}
     * @param hardExclude - optional, specifies items which shouldn't be updated
     */
    updateBySelector(idx, data, hardExclude = []) {
        let row = this.get(idx);
        if (!row) {
            return;
        }

        for (let [k, v] of Object.entries(data)) {
            let el = row.querySelector(k);
            if (hardExclude.includes(k) && el.hasChanged) {
                continue;
            }

            Input.setValue(el, v.value);

            for (let [k1, v1] of Object.entries(v1.meta)) {
                el.dataset[k1] = v1.toString();
            }
        }
    }

    update(idx, data, hardExclude = []) {
        let row = this.get(idx);
        if (!row) {
            return;
        }

        for (let i in data) {
            let el = document.getElementById(`${i}__${idx}__`);
            if (hardExclude.includes(i) && el.hasChanged) {
                continue;
            }

            Input.setValue(el, data[i].value);

            for (let [k, v] of Object.entries(data[i].meta)) {
                el.dataset[k] = v.toString();
            }
        }
    }

    reset(rows = 0, callback = null) {
        this.resetErrors();
        if (!rows) {
            this.rowContainer.innerHTML = null;
            return;
        }

        let entries = this.rowContainer.querySelectorAll('tr');
        if (entries.length <= rows) {
            return;
        }

        for (const [i, v] of Array.from(entries).entries()) {
            if (i >= rows) {
                v.remove();
            }
        }
        if (typeof callback === 'function') {
            callback(this);
        }
    }

    static delete(e) {
        function _delete() {
            let tab = e.closest('tr');
            tab.classList.add(...['section-deleted', 'section-deleted-header']);
            tab.style.display = 'none';
            // document.dispatchEvent(new Event('documentEvt:changed'));
            tab.dispatchEvent(window.evtChanged);
        }

        Alert.question(
            "Czy na pewno usunąć sekcję?",
            "Usunięcie spowoduje utratę wprowadzonych w sekcji danych.",
            () => {
                _delete();
            }
        );
    }

    static undeleteSection(e) {
        let tr = e.closest('tr');
        tr.classList.remove(...['section-deleted', 'section-deleted-header']);
        tr.style.opacity = '1';
        tr.style.display = 'table-row';
        return tr;
    }
}

export default RepeatableTableSection;