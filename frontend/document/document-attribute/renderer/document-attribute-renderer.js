import {DocumentAttributeRendererUtils as RendererUtl} from './document-attribute-renderer-utils';
import DocumentAttributeModel from "../model/document-attribute-model";

import Section from "../component/section/section";

const className = 'DocumentAttributeRenderer';


class DocumentAttributeRenderer {
    constructor(label, content, documentData, errorList = null) {
        this.documentData = documentData;
        this.sectionLabelContainer = label;
        this.sectionContentContainer = content;

        this.model = new DocumentAttributeModel(documentData.type, documentData.status);

        this.className = 'DocumentAttributeRenderer';
        this.data = null;
        this.errorList = errorList;

        this.events = {
            'beforeAttributesRender': new Event('documentAttributeEvt:beforeAttributesRender'),
            'afterAttributesRender': new Event('documentAttributeEvt:afterAttributesRender'),
            'beforeGetModelData': new Event('documentAttributeEvt:beforeGetModelData'),
            'afterGetModelData': new Event('documentAttributeEvt:afterGetModelData'),
            'documentCreated': new Event('documentAttributeEvt:documentCreated')
        };

        this.init();
    }

    async getData() {
        let setData = data => {
            this.data = data;
        };

        return new Promise((resolve, reject) => {
            ajaxCall({
                    method: 'get',
                    url: '/document/api/attribute/',
                    data: {
                        id: this.documentData.id
                    }
                },
                (resp) => {
                    resolve(setData(resp));
                },
                (resp) => {
                    reject(console.log(resp.responseJSON));
                }
            )
        })
    }

    async init() {
        // try {
        if (!window.documentDefinitionMode) {
            // Set container for gathering promises for Promise.all resolving
            window.documentAttributeDataPromises = [];
        }
        document.dispatchEvent(this.events.beforeAttributesRender);
        document.dispatchEvent(this.events.beforeGetModelData);

        // ensure that we have all attribute model structure and basic (not additional ajax call needed) data fetched
        Promise.all([this.model.getModel(), this.getData()]).then(() => {
            document.dispatchEvent(this.events.afterGetModelData);
            this.render();

            // some attributes need to get its values by ajax calls. When it's needed, the ajaxCall Promise will be added to global
            // window.documentAttributePromises array (see input.js: Input.setValue() method)
            // The following code guaranties that
            // afterAttributesRender event is going to be fired after all attribute has its values attached.
            Promise.all(window.documentAttributeDataPromises).then(() => {
                document.dispatchEvent(this.events.afterAttributesRender);
            });
        });
        // } catch (error) {
        //     //todo: log error to global page errors and display error message. Also log error in database and send email to admin
        //     Alert.error(error.name, error.message);
        //     jsUtils.LogUtils.log(error.message, error.stack);
        // }
    }

    // todo: if an item is not editable but ie calculable or modified by action, raise error that it cannot be modified
    static setCalculable(model, idx = null, container = false, errorList = null) {
        if (window.documentDefinitionMode) {
            return;
        }
        let calculableItems = [];
        let changeActionItems = [];

        function _getElement(id) {
            let _id = !(idx === null) ? `${id}__${idx}__` : id;
            if (container) {
                return container.querySelector(`[id="${_id}"]`);
            } else {
                return document.getElementById(_id);
            }
        }

        (function f(snippet) {
            snippet.map(at => {
                if (at.is_section || at.is_column || at.is_combo) {
                    f(at.children);
                } else {
                    // handle special fields
                    // todo: PROBLEM!!! Here when document in definition mode
                    if (at.chart) {
                        let ds = [];

                        at.feature.chart.dataset.map(_e => {
                            ds.push(DocumentAttributeModel.findAttributeByCode(_e.toString(), model));
                        });

                        at.chart.setUp(ds);
                        at.chart.render();

                        return;
                    }

                    let el = _getElement(at.id);

                    if (!el) {
                        return;
                    }

                    if (at?.feature?.calculable) {
                        let filedContainer = el.closest('.form-group');

                        calculableItems.push(el);
                        // handle source elements' value change
                        // todo: handleSourceChanges(sourcesId, idx)

                        at.feature.calculable.sources.map(s => {
                            let sourceElement = _getElement(s);

                            // determine source event type
                            let sourceEventType = sourceElement.classList.contains('date-field') ? 'dp.change' : 'change';
                            let eventType = el.classList.contains('date-field') ? 'dp.change' : 'change';

                            // if the source item value changes, then fire calculable on target
                            sourceElement.addEventListener(sourceEventType, () => {
                                // todo: dodać opis błędu przy polu jak kliknie na przycisk
                                // todo: handleEvent()
                                // if(_g.debug) {
                                //     console.log('-------- document-attribute-renderer.setCalculable() -----------');
                                //     console.log(`action: ${eventType}`);
                                //     console.log(`on element id: ${el.id}`);
                                //     console.log(el);
                                //     console.log(`sources: ${at.feature.calculable.sources}`);
                                //     console.log('-------------------------------')
                                // }
                                let res = eval(at.feature.calculable.calcFunc)(el);
                                jsUtils.Utils.indicateChanged(el);
                                el.dispatchEvent(new Event(eventType));
                            });
                        });

                        // todo: dubel z powyżej - zamienić na funkcję
                        // todo: handleEvent()
                        let res = eval(at.feature.calculable.calcFunc)(el);

                        if (res && res.errmsg) {
                            if (errorList) {
                                if (!errorList[at.code]) {
                                    errorList[at.code] = [];
                                }
                                errorList[at.code].push(res.errmsg);
                            }
                        }
                    }

                    if (at.feature && at.feature.actions && at.feature.actions.change && at.feature.actions.change.triggerOnStartup) {
                        el.dispatchEvent(new Event('change'));
                    }
                }
            });
        })(model);

        calculableItems.map(e => {
            if (e.classList.contains('date-field')) {
                e.dispatchEvent(new Event('dp.change'));
            } else {
                e.dispatchEvent(new Event('change'));
            }
        });
    }

    renderAttributes(section, data, isActive, sectionContentContainer = null) {
        try {
            if (!document.getElementById(`section_${section.id}`)) {
                new RendererUtl().render(
                    section,
                    sectionContentContainer ? sectionContentContainer : this.sectionContentContainer,
                    this.model,
                    this.model.ver,
                    data,
                    isActive);
            }
        } catch (error) {
            //todo: log error to global page errors and display error message. Also log error in database and send email to admin
            Alert.error(error.name, error.message);
            jsUtils.LogUtils.log(error.message, error.stack);
        } finally {
        }
    }

    render() {
        let ul = Section.setLabelItemContainer(this.sectionLabelContainer);

        this.model.model.map((section, idx) => {
            let container = section.container ? document.getElementById(section.container) : ul;
            container.appendChild(Section.renderLabel(section, !idx));

            this.renderAttributes(section,
                this.data,
                !idx,
                section.container ? document.getElementById(section.container) : null);
        });

        DocumentAttributeRenderer.setCalculable(this.model.model, null, null, this.errorList);
        document.dispatchEvent(this.events.documentCreated);
    }
}

export default DocumentAttributeRenderer;
