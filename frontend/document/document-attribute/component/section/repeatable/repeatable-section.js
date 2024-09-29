import {ToolbarUtils, TOOLBAR_BTN} from "../../../../../_core/utils/toolbar-utils";
import Alert from "../../../../../_core/alert";
import RepeatableSectionBase from "./repeatable-section-base";
import DocumentAttributeRenderer from "../../../renderer/document-attribute-renderer";

const className = 'RepeatableSection';

class RepeatableSection extends RepeatableSectionBase {
    constructor(at, renderCallback, level, ver) {
        super(at, renderCallback, level, ver);
        this.rowHeader = jsUtils.Utils.domElement('ul', null, ['nav', 'repeatable-section-tabs', 'nav-tabs', 'repeatable-section-row-header']);
        this.rowContainer = jsUtils.Utils.domElement('div', null, ['tab-content']);
    }

    static length(rowContainer) {
        return rowContainer.querySelectorAll('.tab-pane').length;
    }


    getContainer() {
        let p = jsUtils.Utils.domElement('div', null, ['panel', 'panel-default']);
        let pb = jsUtils.Utils.domElement('div', `${this.at.id}-tab`, ['panel-body', 'repeatable-section-container']);
        let ph = jsUtils.Utils.domElement('div', null, 'panel-heading');

        ph.innerHTML = this.at.name;

        if (!this.readonly()) {
            let phb = jsUtils.Utils.domElement('div', null, null);
            phb.style.cssText = 'float: right';
            phb.innerHTML = `<i id="section_${this.at.id}_addBtn" class="repeatable-section-add-btn fa fa-plus-circle"></i>`;

            phb.addEventListener('click', () => {
                this.add(null, true);
                // document.dispatchEvent(new Event('documentEvt:changed'));
                phb.dispatchEvent(window.evtChanged);
                phb.dispatchEvent(window.evtRepeatableSectionCreated);
            });
            ph.appendChild(phb);
        }
        if (this.at.css_class) {
            this.cl.classList.add(this.at.css_class);
        }

        if (this.at.feature && this.at.feature.style) {
            this.cl.style.cssText = this.at.feature.style;
        }

        pb.appendChild(this.rowHeader);
        pb.appendChild(this.rowContainer);

        p.appendChild(ph);
        p.appendChild(pb);

        this.cl.appendChild(p);

        return this.cl;
    }

    add(data, visible = false) {
        let idx = this.getTabLength();
        let tab = this.addRepeatableSectionHeader(idx);
        let row = this.addRepeatableSectionRowContainer(idx);

        this.rowHeader.appendChild(tab);
        this.rowContainer.appendChild(row);

        // generate repeatable section fields
        this.renderCallback(this.at.children, row.getElementsByTagName('fieldset')[0], idx, this.level, this.ver);
        DocumentAttributeRenderer.setCalculable(this.at.children, idx, null);
        DocumentAttributeRenderer.dep

        let a = tab.getElementsByTagName('a')[0];
        if (visible) {
            for(let i of Array.from(this.rowHeader.querySelectorAll('ul li.active'))) {
                i.classList.remove('active');
            }

            for(let i of Array.from(this.rowContainer.querySelectorAll('div.active'))) {
                i.classList.remove(...['active']);
            }

            tab.classList.add('active');
            row.classList.add('active');

            // $(a).tab('show');
        }
        return a;
    }

    static delete(e, id) {
        function _delete() {
            let tab = document.getElementById(id);
            tab.classList.add('section-deleted');

            let li = e.target.closest('li');
            li.style.display = 'none';
            tab.style.display = 'none';

            let prev = li.previousElementSibling;
            let next = li.nextElementSibling;

            if (prev) {
                prev.getElementsByTagName('a')[0].click();
            } else if (next) {
                next.getElementsByTagName('a')[0].click();
            }
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

    static undeleteSection(e, id) {
        //todo: implement section undeletion
    }

    addRepeatableSectionHeader(idx) {
        let li = jsUtils.Utils.domElement('li', null, 'tab-pane');
        let a = jsUtils.Utils.domElement('a');

        let id = `${this.at.id}__${idx}__tab`;

        a.classList.add('repeatable-section-tab-header');
        a.dataset['toggle'] = 'tab';
        a.dataset['href'] = id;
        a.setAttribute('href', `#${id}`);
        a.text = this.at.name;
        li.appendChild(a);

        if (!this.readonly()) {
            let tbDelBtn = ToolbarUtils.deleteBtn(TOOLBAR_BTN.sm);
            tbDelBtn.addEventListener('click', (e) => {
                RepeatableSection.delete(e, id)
            });

            li.appendChild(tbDelBtn);
        }

        return li;
    }

    addRepeatableSectionRowContainer(idx) {
        let row = document.createElement('div');
        let id = `${this.at.id}__${idx}__tab`;
        // row.classList.add('row');
        let tabPane = document.createElement('div');
        tabPane.id = id;
        tabPane.classList.add(...['tab-pane', 'repeatable-section-tab', 'fade', 'in']);
        // if (active) {
        //     tabPane.classList.add('active');
        // }
        tabPane.appendChild(row);
        let fieldset = document.createElement('fieldset');
        fieldset.classList.add('repeatable-section-tab-content');
        row.appendChild(fieldset);

        return tabPane;
    }
}

export default RepeatableSection;