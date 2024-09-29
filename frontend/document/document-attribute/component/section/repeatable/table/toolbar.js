import RepeatablePredefinedTableSectionModal from "./repeatable-predefined-table-section-modal";

class Toolbar {
    constructor(section) {
        this.section = section;
        this.buttonContainer = jsUtils.Utils.domElement('div', '', 'repeatable-table-section-toolbar-button-container');
        this.item = this._getToolbar();
        this.item.appendChild(this.buttonContainer);

    }

    addButton(id, classname, iconClass, tooltip = null, callback = null, fn = null) {
        let phb = document.createElement('div');
        phb.style.cssText = 'float: right';
        phb.innerHTML = `<i id="${id}_addBtn" class="${classname} ${iconClass}"></i>`;

        if (tooltip) {
            $(phb).tooltip({title: tooltip});
        }

        if (typeof callback === 'function') {
            phb.addEventListener('click', (phb) => {
                callback(phb);
            });
        }

        if (fn) {
            phb.addEventListener('click', (phb) => {
                eval(fn)(phb);
            });
        }

        this.buttonContainer.appendChild(phb);
    }

    _getToolbar() {
        // panel heading with toolbar buttons
        let ph = document.createElement('div');
        ph.classList.add('panel-heading');
        ph.innerHTML = this.section.at.name;

        //-- add regular sectionAdd Btn
        if (!this.section.readonly()) {
            this.addButton(`section_${this.section.at.id}_addBtn`,
                'repeatable-section-add-btn',
                'fa fa-plus-circle',
                'Dodaj sekcję',
                (el) => {
                    this.section.add(null, this.section.rowContainer, true, null);
                    el.target.dispatchEvent(window.evtChanged);
                });
        }

        // add custom section action buttons
        if (this.section?.at?.feature?.toolbar?.buttons) {
            for (let i of this.section.at.feature.toolbar.buttons) {
                this.addButton(`section_${this.section.at.id}_${i.name}`, i.selector, i.icon, i.title, '', i.fn);
            }
        }

        // predefined list modal handling
        if (!this.section.readonly() && this.section?.at?.feature?.predefined) {
            let plb = document.createElement('div');
            plb.style.cssText = 'float: right';
            plb.innerHTML = `<i id="section_${this.section.at.id}_predefinedListAddBtn" class="repeatable-section-predefined-list-add-btn fas fa-list"></i>`;

            plb.addEventListener('click', () => {
                let modal = $(`#${this.section.at.id}_modal`);
                modal.modal('show');

                //    set the status of the modal list checkboxes
                //    todo: move it to the repeatable-table-section.js file as control owner. Handle the bs.dialog.show like trigger
                modal.find('table tbody tr input[type="checkbox"]').each((i, e) => {
                    e.checked = false;
                    for (let i of Array.from(this.section.cl.querySelectorAll('table tbody tr:not(.section-deleted) input[data-type="__rowid__"] '))) {
                        if (i.value == e.id) {
                            e.checked = true;
                        }
                    }
                });
            });

            ph.appendChild(plb);
            // add predefined list modal dialog
            this.section.cl.appendChild(
                new RepeatablePredefinedTableSectionModal(
                    this.section.at,
                    this.section.rowContainer,
                    this.section.renderCallback,
                    this.section.level,
                    this.section.ver).getPredefinedModal());
        }

        return ph;
    }
}

export {Toolbar};