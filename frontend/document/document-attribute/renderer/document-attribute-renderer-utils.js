import FieldRenderer from "../../js/document-field-renderer";
import {SystemException} from "../../../_core/exception";
import RepeatableSection from "../component/section/repeatable/repeatable-section";
import RepeatableTableSection from "../component/section/repeatable/table/repeatable-table-section";
import Section from "../component/section/section";
import Column from "../component/column/column";
import TabSection from "../component/section/tab-section";
import Combo from "../component/combo/combo";
import {DocumentAttributeInstalmentScheduleRepeatableSection} from "../instalment-schedule/document-attribute-instalment-schedule-repeatable-section";

const className = 'DocumentAttributeRendererUtils';

class DocumentAttributeRendererUtils {

    constructor(sectionCallback = null, columnCallback = null, fieldCallback = null) {
        this.sectionCallback = sectionCallback;
        this.columnCallback = columnCallback;
        this.fieldCallback = fieldCallback;
        // this.events = {
        //     'sectionCreated': 'documentAttributeEvt:sectionCreated',
        //
        // }
    }

    static _getRepeatableSectionClass(at, f, level, ver) {
        return at.selector_class == 'instalment-schedule' ?
            new DocumentAttributeInstalmentScheduleRepeatableSection(at, DocumentAttributeRendererUtils.fTable, level, ver) :
            at.is_table ?
                new RepeatableTableSection(at, DocumentAttributeRendererUtils.fTable, level, ver) :
                new RepeatableSection(at, f, level, ver);
    }

    static _getRepeatableSectionTabLength(at, data) {
        let repeatableLength = data ? (data[at.id] ? data[at.id]?.value : 0) : 0;
        if (repeatableLength === "undefined" || repeatableLength == null) {
            throw new SystemException(`[${className}][_render] repreatable section length undefined`);
        }
        return repeatableLength;
    }

    // todo: docelowo usunąć fTable i zostawić tylko f - inaczej nie zrobi się zagnieżdzonych sekcji powtarzalnych
    static fTable(model, data, sc, rIdx, level, predefined = null, ver = null) {
        model.map(at => {
            if (at.is_section) {
                DocumentAttributeRendererUtils.fTable(at.children, data, sc, rIdx, level, predefined, ver);

            } else if (at.is_column) {
                let td = document.createElement('td');

                sc.appendChild(td);
                DocumentAttributeRendererUtils.fTable(at.children, data, td, rIdx, level, predefined, ver);

            } else {
                let defaultValue = null;
                let defaultLabel = null;

                if (predefined) {
                    if (at.id == predefined.rowid) {
                        defaultValue = predefined.id

                    } else if (at.id == predefined.rowlabel) {
                        defaultValue = predefined.label

                    } else if (at.id == predefined.field) {
                        defaultValue = predefined.text;
                        if (predefined.label) {
                            defaultLabel = predefined.label;
                        }
                    }
                }

                let itemVer = {};
                if (ver && ver.hasOwnProperty(at.id)) {
                    itemVer = ver[at.id];
                }
                sc.appendChild(FieldRenderer.render(
                    at, data, rIdx, true, false, defaultValue, defaultLabel, null, itemVer).fieldContainer
                );
            }
        });
    }


    _render(model, sc, data, ver) {
        let _this = this;

        (function f(model, sc, rIdx, level, ver = null) {
            model.map(at => {
                if (at.is_section) {
                    if (at.feature?.repeatable) {
                        let repeatableSection = DocumentAttributeRendererUtils._getRepeatableSectionClass(at, f, level + 1, ver);
                        let cl = repeatableSection.getContainer();
                        sc.appendChild(cl);

                        // generate section rows according to repeatable section data.
                        // Data must be an array structure, even if only one row
                        for (let i = 0; i < DocumentAttributeRendererUtils._getRepeatableSectionTabLength(at, data); i++) {
                            repeatableSection.add(data, !i);
                        }

                    } else {
                        if (at.feature && at.feature.tab) {
                            let cl = TabSection.renderTabSection(at, null, rIdx);
                            let tc = cl.tabContent;

                            sc.appendChild(cl.tabSection);

                            at.children.map((e, idx) => {
                                // render tab pane for section
                                let pane = TabSection.renderTabPane(e, !idx, ver, rIdx);
                                tc.appendChild(pane);
                                f(e.children, pane, rIdx, level, ver);
                            });

                        } else {
                            let cl = Section.renderSection(at);
                            sc.appendChild(cl);
                            f(at.children, cl, rIdx, level, ver);
                        }
                    }

                } else if (at.is_column) {
                    let cl = Column.render(at, _this.columnCallback);
                    sc.appendChild(cl);
                    f(at.children, cl, rIdx, level, ver);

                } else if (at.is_combo) {
                    let cl = Combo.render(at);
                    sc.appendChild(cl.clContainer);
                    f(at.children, cl.container, rIdx, level, ver);

                    for (let i of Array.from(cl.container.querySelectorAll('input, select, textarea'))) {
                        i.addEventListener('change', (e) => {
                            Combo.getContent(cl, at);
                        });
                    }
                    Combo.getContent(cl, at);

                } else {
                    let itemVer = {};
                    if (ver && ver.hasOwnProperty(at.id)) {
                        itemVer = ver[at.id]
                    }
                    sc.appendChild(FieldRenderer.render(
                        at, data, rIdx, true, true, null, null, _this.fieldCallback, itemVer).fieldContainer
                    );
                }
            })
        })(model, sc, null, 0, ver);
    }

    render(section, sectionContentContainer, model, ver, data, isActive) {
        let sc;

        if (section) {
            sc = Section.renderMainSection(section, isActive);
        }
        sectionContentContainer.appendChild(sc);

        this._render(section.children, sc, data, ver);
    }
}

export {DocumentAttributeRendererUtils};

