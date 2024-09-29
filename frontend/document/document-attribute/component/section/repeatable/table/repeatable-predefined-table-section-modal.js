import Alert from "../../../../../../_core/alert";
import ajaxCall from "../../../../../../_core/ajax";
import IdUtils from "../../../../../../_core/utils/id-utils";
import RepeatableTableSection from "./repeatable-table-section";
import {SystemException} from "../../../../../../_core/exception";
import HtmlUtils from "../../../../../../_core/utils/html-utils";

const className = 'RepeatablePredefinedTableSectionUtils';

class RepeatablePredefinedTableSectionModal {
    constructor(at, rowContainer, renderCallback, level) {
        this.rowContainer = rowContainer; // document.getElementById(at.id); // the table body gathering added row of data
        this.renderCallback = renderCallback;
        this.level = level;
        this.at = at;
        this.predefinedModal = null;
        this.opts = {
            predefinedNavBtnActiveClass: 'predefined-nav-btn-active'
        };

        this.defaultItemText = 'Wprowadź własny tekst...';
        this.defaultItemLabel = 'Wprowadź własną etykietę...';

        this.addNavBtn = null;
        this.editNavBtn = null;
        this.saveNavBtn = null;
        this.toggleLblNavBtn = null;

        this.tblBody = null;
        this.predefinedModalHtml =
            '<div class="modal-dialog" style="width: 1000px;" role="document">' +
            '    <div class="modal-content">' +
            '      <div class="modal-header">' +
            // '        <button type="button" class="close navmodal-button" data-dismiss="modal" aria-label="Close"><span aria-hidden="true"><i class="fa fa-times"></i></span></button>' +
            '        <button id="showSelectedPredefinedListBtn" type="button" class="modal-navbutton show-selected-navbutton"><span aria-hidden="true"><i class="fas fa-tasks"></i></span></button>' +
            '        <button id="showLabelsOnlyPredefinedListBtn" type="button" class="modal-navbutton show-labels-only-navbutton"><span aria-hidden="true"><i class="fas fa-tag"></i></span></button>' +
            '        <button id="editPredefinedListBtn" type="button" class="modal-navbutton edit-navbutton"><span aria-hidden="true"><i class="fa fa-edit"></i></span></button>' +
            '        <button id="addPredefinedListBtn" type="button" class="modal-navbutton add-navbutton" style="display: none;"><span aria-hidden="true"><i class="fa fa-plus-circle"></i></span></button>' +
            '        <button id="savePredefinedListBtn" type="button" class="modal-navbutton save-navbutton" style="display: none;"><span aria-hidden="true"><i class="fa fa-check-circle"></i></span></button>' +
            '        <h4 class="modal-title">Dostępne warunki</h4>' +
            '      </div>' +
            '      <div class="modal-body">' +
            '<div class="predefined-list-container">' +
            '<table class="table predefined-list">' +
            '<tbody></tbody>' +
            '</table>' +
            '</div>' +
            '</div>' +
            '      <div class="modal-footer">' +
            '        <button type="button" class="btn btn-default" data-dismiss="modal">Zamknij</button>' +
            // '        <button id="addPredefinedBtn" type="button" class="btn btn-primary">Zatwierdź</button>' +
            '      </div>' +
            '    </div>' +
            '  </div>';

        this.saveList = () => {
            Alert.question('Czy na pewno zapisać zmiany?', '', () => {
                let list = [];
                Array.from(this.tblBody.getElementsByTagName('tr')).map(e => {
                    list.push({
                        id: e.dataset['id'],
                        text: e.getElementsByClassName('modal-predefined-text')[0].innerText,
                        label: e.getElementsByClassName('modal-predefined-label')[0].innerText
                    });
                });

                ajaxCall(
                    {
                        method: 'post',
                        url: _g.document.attribute.urls.predefinedUrl,
                        data: {
                            id: this.at.id,
                            list: JSON.stringify(list)
                        }
                    },
                    (resp) => {
                        // remove modified flag class from items
                        Array.from(this.tblBody.querySelectorAll('.predefined-item-modified')).map(e => {
                            e.classList.remove('predefined-item-modified');
                        });

                        // add checkbox and its listener to the new items
                        Array.from(this.tblBody.querySelectorAll('tr[data-status="NEW"]')).map(e => {
                            this._addCheckBtn(e.getElementsByClassName('predefined-action-item-container')[0], e.dataset['id']);
                            delete e.dataset.status;
                        });


                        this.editNavBtn.dispatchEvent(new Event('click'));
                        Alert.info('Zmiany zostały zapisane');
                    },
                    (resp) => {
                        Alert.error(resp.responseJSON.errmsg);
                    },
                    () => {
                    }
                )
            })
        };

        this.toggleSelected = () => {
            this.toggleNavBtn(this.toggleSelectedNavBtn, (el) => {
                let active = el.dataset['active'] === 'true';
                Array.from(this.tblBody.getElementsByTagName('tr')).map(e => {
                    if (active && !e.querySelector('.predefined-item-check').checked) {
                        e.style.display = 'none';
                    } else {
                        e.style.removeProperty('display');
                    }
                });
            })
        };

        this.toggleLabels = () => {
            this.toggleNavBtn(this.toggleLblNavBtn, (el) => {
                let active = el.dataset['active'] === 'true';
                Array.from(this.tblBody.getElementsByTagName('tr')).map(e => {
                    let _e = e.getElementsByClassName('modal-predefined-text')[0];
                    if (active) {
                        _e.style.display = 'none';
                    } else {
                        _e.style.removeProperty('display');
                    }
                });
            });
        };

        this.init();
    }

    toggleNavBtn(el, callback = null) {
        if (el.dataset['active'] === 'true') {
            el.classList.remove(this.opts.predefinedNavBtnActiveClass);
            el.dataset['active'] = 'false';
        } else {
            el.classList.add(this.opts.predefinedNavBtnActiveClass);
            el.dataset['active'] = 'true';
        }
        if (typeof callback === 'function') {
            callback(el);
        }
    };

    toggleEditNavButton() {
        let active = this.editNavBtn.dataset['active'] === "true";

        this.toggleNavBtn(this.editNavBtn, () => {
            this.addNavBtn.style.display = active ? 'none' : 'inherit';
            this.saveNavBtn.style.display = active ? 'none' : 'inherit';
            Array.from(this.predefinedModal.getElementsByClassName('predefined-list')[0].querySelectorAll("tr")).map((row) => {
                let text = row.getElementsByTagName('span')[0];
                let label = row.querySelector('div.modal-predefined-label');
                let chk = row.querySelector('input[type="checkbox"]');
                let delBtn = row.getElementsByClassName('predefined-item-delete-btn')[0];
                let revertBtn = row.getElementsByClassName('predefined-item-revert-btn')[0];
                let isModified = row.getElementsByClassName('predefined-item-modified').length;

                text.contentEditable = active ? "false" : "true";
                label.contentEditable = active ? "false" : "true";
                if (chk) {
                    chk.style.display = active ? "inherit" : "none";
                }
                delBtn.style.display = (chk && chk.checked) ? "none" : active ? "none" : "inherit";
                revertBtn.style.display = active ? 'none' : isModified ? 'inherit' : 'none';

                if (active) {
                    text.classList.remove('content-editable');
                    label.classList.remove('content-editable');

                } else {
                    text.classList.add('content-editable');
                    label.classList.add('content-editable');
                }
            });
        });
    }

    checkBtnCallback(chk) {
        let tableRow = this.rowContainer.querySelector(`input[data-type="__rowid__"][value="${chk.id}"]`);
        let listRow = chk.closest('tr');
        if (!listRow) {
            throw new SystemException(`[${className}][checkBtnCallback]: nie znaleziono kontenera dla wpisu`);
        }
        let txtItem = listRow.getElementsByClassName('modal-predefined-text')[0];
        let lblItem = listRow.getElementsByClassName('modal-predefined-label')[0];

        if (!tableRow && chk.checked) {
            // todo: make the function from it
            let tr = this.rowContainer.querySelectorAll('tr');

            let tabLength = tr ? tr.length : 0;
            let row = RepeatableTableSection.addRowContainer(this.at.name, `${this.at.id}__${tabLength}__tab`);

            // render row items
            this.renderCallback(this.at.children, null, row, tabLength, this.level + 1,
                {
                    id: chk.id,
                    text: txtItem.innerText,
                    label: lblItem.innerText,
                    field: this.at.feature.predefined.field,
                    rowlabel: this.at.feature.predefined.rowlabel,
                    rowid: this.at.feature.predefined.rowid
                });

            this.rowContainer.appendChild(row);

        } else if (tableRow && !chk.checked) {
            RepeatableTableSection.delete(tableRow);

        } else if (tableRow && chk.checked) {
            let tr = RepeatableTableSection.undeleteSection(tableRow);

            // set new values to the undeleted section row
            let txt = tr.querySelector(`[data-code="${this.at.feature.predefined.field}"]`);
            txt.value = txtItem.innerText;
            console.log('label', txt.closest('div').getElementsByTagName('label')[0]);
            txt.closest('div').getElementsByTagName('label')[0].innerText = lblItem.innerText;
            tr.querySelector(`[data-code="${this.at.feature.predefined.rowlabel}"]`).value = lblItem.innerText;
        }
    }

    _addCheckBtn(container, id) {
        if (!id) {
            jsUtils.LogUtils.log(`[${className}][_addCheckBtn]: id jest pusty`);
            return;
        }

        let chk = document.createElement('input');
        container.appendChild(chk);
        chk.type = 'checkbox';
        chk.classList.add('predefined-item-check');
        chk.id = id;

        chk.addEventListener('change', () => {
            this.checkBtnCallback(chk);
        });

        return chk;
    }

    static _addContainers(row) {
        let chkContainer = document.createElement('td');
        chkContainer.classList.add('predefined-action-item-container');
        let txtContainer = document.createElement('td');
        txtContainer.classList.add('predefined-text-label-container');
        row.appendChild(chkContainer);
        row.appendChild(txtContainer);

        return {chkContainer: chkContainer, txtContainer}
    }

    _addDelBtn(container) {
        let delBtn = document.createElement('i');
        container.appendChild(delBtn);
        delBtn.classList.add(...['fa', 'fa-times', 'predefined-item-delete-btn']);
        delBtn.style.display = 'none';
        delBtn.addEventListener('click', e => {
            Alert.questionWarning(
                'Czy na pewno usunąć wpis',
                'Wpis zostanie usunie usunięty jedynie jeśli nie był wykorzystany w żadnym z dokumentów',
                (el) => {
                    let tr = el.closest('tr');
                    let chk = tr.getElementsByClassName('predefined-item-check')[0];
                    ajaxCall(
                        {
                            method: 'delete',
                            url: _g.document.attribute.urls.predefinedUrl,
                            data: {
                                id: chk.id,
                                attributeId: this.at.id,
                                documentId: _g.document.id
                            }
                        },
                        (resp) => {
                            tr.remove();
                            Alert.info('Wpis został usunięty');
                        })
                }, e.target)
        })
    }

    _addRevertBtn(container) {
        let revertBtn = document.createElement('i');
        container.appendChild(revertBtn);
        revertBtn.classList.add(...['fas', 'fa-history', 'predefined-item-revert-btn']);
        revertBtn.style.display = 'none';

        revertBtn.addEventListener('click', evt => {
            Alert.question('Czy na pewno przywrócić wersję początkową?', '', () => {
                let tr = evt.target.closest('tr');
                let txt = tr.getElementsByClassName('modal-predefined-text')[0];
                let lbl = tr.getElementsByClassName('modal-predefined-label')[0];
                txt.innerText = HtmlUtils.escapeScriptTag(txt.dataset['originaltext']);
                lbl.innerText = HtmlUtils.escapeScriptTag(lbl.dataset['originaltext']);

                Array.from(this.tblBody.getElementsByClassName('predefined-item-modified')).map(e => {
                    e.classList.remove('predefined-item-modified');
                });
                evt.target.style.display = 'none';
            });
        });
    }

    static _addLabel(container, e) {
        let lbl = document.createElement('div');
        container.appendChild(lbl);
        lbl.addEventListener("input", RepeatablePredefinedTableSectionModal.setPredefinedModified);
        lbl.classList.add('modal-predefined-label');
        lbl.innerText = e.label;
        lbl.dataset['originaltext'] = e.label;
    }

    static _addText(container, e) {
        let txt = document.createElement('span');
        container.appendChild(txt);

        txt.classList.add('modal-predefined-text');
        txt.addEventListener("input", RepeatablePredefinedTableSectionModal.setPredefinedModified);
        txt.innerText = e.text;
        txt.dataset['originaltext'] = e.text;
    }

    renderPredefinedList(l = null) {
        let list = l ? l : this.at.feature.predefined.list;
        list.map((e, idx) => {
            let listRow = document.createElement('tr');
            listRow.dataset['id'] = e.id;
            this.tblBody.appendChild(listRow);

            let containers = RepeatablePredefinedTableSectionModal._addContainers(listRow);

            this._addCheckBtn(containers.chkContainer, e.id);
            this._addDelBtn(containers.chkContainer);
            this._addRevertBtn(containers.chkContainer);
            RepeatablePredefinedTableSectionModal._addLabel(containers.txtContainer, e);
            RepeatablePredefinedTableSectionModal._addText(containers.txtContainer, e);
        });
    }

    static setPredefinedModified(e) {
        let el = e.target;
        let revertBtn = el.closest('tr').querySelector('.predefined-item-revert-btn');
        if (el.innerText !== el.dataset['originaltext']) {
            el.classList.add('predefined-item-modified');
            revertBtn.style.display = 'inherit';

        } else {
            el.classList.remove('predefined-item-modified');
            revertBtn.style.display = 'none';
        }
    };

    renderPredefinedModal() {
        this.predefinedModal = document.createElement('div');
        this.predefinedModal.classList.add(...['modal', 'fade']);
        this.predefinedModal.innerHTML = this.predefinedModalHtml;
        this.predefinedModal.id = `${this.at.id}_modal`;
        this.predefinedModal.classList.add(...['modal', 'fade']);
        this.predefinedModal.tabIndex = "-1";
        this.predefinedModal.role = 'dialog';

        this.tblBody = this.predefinedModal.querySelector('.predefined-list-container table tbody');

        // add modal nav buttons
        this.addNavBtn = this.predefinedModal.getElementsByClassName('add-navbutton')[0];
        this.editNavBtn = this.predefinedModal.getElementsByClassName('edit-navbutton')[0];
        this.saveNavBtn = this.predefinedModal.getElementsByClassName('save-navbutton')[0];
        this.toggleSelectedNavBtn = this.predefinedModal.getElementsByClassName('show-selected-navbutton')[0];
        this.toggleLblNavBtn = this.predefinedModal.getElementsByClassName('show-labels-only-navbutton')[0];

        this.editNavBtn.dataset['active'] = "false";
        this.toggleSelectedNavBtn.dataset['active'] = "false";
        this.toggleLblNavBtn.dataset['active'] = "false";

        // add actions to modal nav buttons
        this.addNavBtn.addEventListener('click', () => {
            let tr = this.tblBody.querySelector('tr').cloneNode(true);
            tr.dataset['id'] = Date.now();
            tr.dataset['status'] = 'NEW';
            tr.getElementsByClassName('predefined-item-check')[0].remove(); // remove checkbox to prevent against adding when not saved into db
            let txt = tr.getElementsByClassName('modal-predefined-text')[0];
            let lbl = tr.getElementsByClassName('modal-predefined-label')[0];
            let del = tr.getElementsByClassName('predefined-item-delete-btn')[0];
            del.addEventListener('click', () => {
                Alert.questionWarning('Czy na pewno usunąć wpis?', '', () => {
                    tr.remove();
                });
            });
            txt.innerText = this.defaultItemText;
            txt.classList.add('predefined-item-modified');
            lbl.innerText = this.defaultItemLabel;
            lbl.classList.add('predefined-item-modified');

            this.tblBody.appendChild(tr);

            tr.scrollIntoView();
        });

        this.editNavBtn.addEventListener('click', () => {
            this.toggleEditNavButton();
        });

        this.toggleSelectedNavBtn.addEventListener('click', () => {
            this.toggleSelected();

        });

        this.toggleLblNavBtn.addEventListener('click', () => {
            this.toggleLabels();
        });

        this.saveNavBtn.addEventListener('click', () => {
            this.saveList();
        });

        // render list elements
        this.renderPredefinedList();
    }

    getPredefinedModal() {
        return this.predefinedModal;
    }

    getPredefinedModalBody() {
        return this.predefinedModal.getElementsByClassName("modal-body")[0];
    }

    init() {
        if (typeof this.renderCallback !== 'function') {
            throw new SystemException('renderCallback musi być funkcją');
        }
        this.renderPredefinedModal(this.at.id);
    }
}

export default RepeatablePredefinedTableSectionModal;