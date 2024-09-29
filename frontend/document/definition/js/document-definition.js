import DocumentAttributeModel from "../../document-attribute/model/document-attribute-model";
import Column from "./column/column";
import Field from "./field/field";
import Section from "../../document-attribute/component/section/section";
import {DocumentAttributeRendererUtils} from "../../document-attribute/renderer/document-attribute-renderer-utils";
import Sortable from 'sortablejs';

import ItemToolbar from "./buttons/item-toolbar";
import DocumentDefinitionContextMenu from "./section/documentDefinitionMenu/document-definition-context-menu";
import {SystemException} from "../../../_core/exception";

const className = 'DocumentDefinition';

class DocumentDefinition {
    constructor(containerId, documentType) {
        this.container = document.getElementById(containerId);
        this.sectionLabelContainer = document.getElementById('documentSectionLabelContainer');
        this.sectionContentContainer = document.getElementById('sectionContentContainer');
        this.sectionLabelItemContainer = null;

        this.model = new DocumentAttributeModel(documentType, null, false);
        this.section = new Section();
        this.column = new Column();
        this.field = new Field();
        this.menu = new DocumentDefinitionContextMenu('#contextMenu');

        this.itemPrpoertiesModal = document.getElementById('documentDefinitionItemPropertiesModal');

        this.attributeTypes = [];

        this.init();
    }

    getAttributeTypes() {
        return new Promise((resolve, reject) => ajaxCall({
                method: 'get',
                url: '/attribute/api/',
                data: {action: '__GET_LIST__'}
            }).then(
                (data) => {
                    this.attributeTypes = data;
                    resolve();
                },
                (err) => {
                    reject();
                    throw new SystemException(`${className}:getAttributeTypes: ${err}`);
                })
        )
    }

    _resetItemPropertiesModal() {

    }

    _fillItemPropertiesModal() {
    }

    _showItemPropertiesModal() {
        $(this.itemPrpoertiesModal).modal();
    }

    editProperties() {
        this._resetItemPropertiesModal();
        this._fillItemPropertiesModal();
        this._showItemPropertiesModal();
    }

    init() {
        window.documentDefinitionMode = true;

        Promise.all([this.model.getModel(), this.getAttributeTypes()]).then(() => {
            let attributeTypeList =  this.itemPrpoertiesModal.querySelector('.document-definition-attribute-type-list');
            for(let at of this.attributeTypes) {
                let opt = new Option(at.name, at.id);
                attributeTypeList.appendChild(opt);
            }

            this.sectionLabelItemContainer = Section.setLabelItemContainer(this.sectionLabelContainer);
            this.render();

            // set scrollable functionality for section labels
            new Sortable(document.getElementById('labelItemContainer'), {
                handle: '.handle-label', // handle's class
                ghostClass: 'sortable-label-swap',
                animation: 150,
                scroll: true,
            });

            Array.from(document.getElementsByClassName('subsection-container')).map(e => {
                //e.setAttribute('tabindex', '0');
                new Sortable(e, {
                    handle: '.handle-column', // handle's class
                    group: e.id,
                    ghostClass: 'sortable-label-swap',
                    animation: 150,
                    scroll: true,
                    onStart: evt => {

                    },
                    onEnd: evt => {
                        var itemEl = evt.item;  // dragged HTMLElement
                        console.log(evt.item,
                            evt.to,    // target list
                            evt.from,  // previous list
                            // evt.oldIndex,  // element's old index within old parent
                            evt.newIndex,  // element's new index within new parent
                            //evt.oldDraggableIndex, // element's old index within old parent, only counting draggable elements
                            // evt.newDraggableIndex, // element's new index within new parent, only counting draggable elements
                            // evt.clone, // the clone element
                            //evt.pullMode
                        );  // when item is in another sortable: `"clone"` if cloning, `true` if moving
                    }
                });
            });

            //add sortable for elements inside columns (column-container) so for every simple item
            Array.from(document.getElementsByClassName('column-container')).map(e => {
                e.setAttribute('tabindex', 0);
                new Sortable(e, {
                    handle: '.toolbar-handle-btn', // handle's class
                    group: 'column-container',
                    ghostClass: 'sortable-label-swap',
                    animation: 150,
                    scroll: true,
                    onStart: evt => {

                    },
                    onMove: evt => {
                        if (evt.related.classList.contains('heading-title')) {
                            return false;
                        }
                    },
                    onEnd: evt => {
                        var itemEl = evt.item;  // dragged HTMLElement
                        console.log(evt.item,
                            evt.to,    // target list
                            evt.from,  // previous list
                            // evt.oldIndex,  // element's old index within old parent
                            evt.newIndex,  // element's new index within new parent
                            //evt.oldDraggableIndex, // element's old index within old parent, only counting draggable elements
                            // evt.newDraggableIndex, // element's new index within new parent, only counting draggable elements
                            // evt.clone, // the clone element
                            //evt.pullMode
                        );  // when item is in another sortable: `"clone"` if cloning, `true` if moving
                    }
                });
            });

            Array.from(document.getElementById('sectionContentContainer').getElementsByTagName('hr')).map(e => {
                e.tabIndex = 0;
            });

            let itemBtnContainer = ItemToolbar.render(null, {remove: true, edit: true});


            itemBtnContainer.querySelector('.edit-icon').addEventListener('click', () => {
                this.editProperties();
            });

            $(document).on('focus', '.form-control, .column-container .document-sortable-element', e => {
                let cnt = e.target.closest('.form-group');
                if (!cnt) {
                    cnt = e.target.closest('.document-sortable-element');
                }
                if (cnt) {
                    cnt.appendChild(itemBtnContainer);
                }
            });

            // $(document).on('blur', '.form-control', e => {
            //     setTimeout(() => {
            //         console.log(e.target);
            //         console.log(document.activeElement);
            //         if (!document.activeElement.classList.contains('handle-field')) {
            //             e.target.closest('.form-group').removeChild(itemBtnContainer);
            //         }
            //     }, 150);
            //
            // });

            $(document).on('mousedown', 'select:not(.document-definition-attribute-type-list)', e => {
                e.preventDefault();
                e.target.focus();
            });

            $(document).on('contextmenu', e => {
                if (e.target.classList.contains('column-container') || e.target.classList.contains('subsection-container')) {
                    this.menu.show(e);
                } else {
                    $('#contextMenu').hide();
                }
                return false;
            });

            $(document).on('click', '*', e => {
                if (e.target?.parentElement?.id !== 'contextMenu') {
                    $('#contextMenu').hide();
                }
            })
        });
    }

    render() {
        this.model.model.map((section, idx) => {
            this.sectionLabelItemContainer.appendChild(Section.renderLabel(
                section, !idx,
                {fn: ItemToolbar.render, opt: {handle: {type: 'V'}, edit: true, remove: false, icon: 'handle-label'}}
            ));

            let da = new DocumentAttributeRendererUtils(
                null,
                null,
                {
                    fn: (cnt, opt) => {
                        cnt.appendChild(jsUtils.Utils.domElement('div', null, 'handle-field'));
                    }
                    , opt: {handle: {type: 'H'}, remove: false, icon: 'handle-column'}
                },
            );
            da.render(section, this.sectionContentContainer, this.model.model, null, !idx);
        });
    }
}

export default DocumentDefinition;