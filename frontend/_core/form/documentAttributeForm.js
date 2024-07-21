import {SystemException} from "../exception";
import Input from "../input";

const INPUT_TYPES = ['text', 'password', 'number', 'email', 'tel', 'url', 'search', 'date', 'datetime', 'datetime-local', 'time', 'month', 'week'];

class DocumentAttributeForm {
    static collectMeta(el) {
        if (!jsUtils.Utils.isDomElement(el)) {
            return {}
        }

        let meta = {}

        for (let [k, v] of Object.entries(el.dataset)) {
            if(k.indexOf('__meta__') !== -1) {
                meta[k.replace('__meta__', '')] = v;
            }
        }

        return meta;
    }

    static collectData(documentModel, callback = null, attributeSetType = 'ATTR') {

        let attributeData = {};
        let repeatableSections = {};
        let isRepeatable = false;
        let repeatableSectionId = null;
        let repeatableSectionRowIdx = null;

        (function f(model, level) {
            if (level === 1) {
                isRepeatable = false;
                repeatableSectionId = null;
            }

            model.map(e => {
                // let eId = attributeSetType === 'ATTR' ? e.id : e.code;
                let eId = e.id;

                if (e.is_section || e.is_column || e.is_combo) {
                    let _level = level;
                    if (e.is_section && e?.feature?.repeatable) {
                        let rSecTab = document.getElementById(`${e.id}-tab`);
                        let rSec = rSecTab.querySelectorAll(".repeatable-section-tab:not(.section-deleted)");
                        isRepeatable = true;
                        _level += 1;
                        attributeData[eId] = {value: rSec.length, meta: {}};
                        repeatableSections[eId] = {};
                        repeatableSectionId = eId;

                        for (let i of Array.from(rSec)) {
                            // get the index of repeatable section tab (id in the form of 'ID_NUMBER__IDX__tab': ie.: 1234__0__tab)
                            repeatableSectionRowIdx = i.id.match(/\d+__(\d+)__tab/)[1];
                            f(e.children, _level);
                        }
                        return false;
                    }

                    f(e.children, level);
                    return false;
                }

                if (e.attribute.no_data) {
                    return false;
                }

                let el = isRepeatable ? document.getElementById(`${eId}__${repeatableSectionRowIdx}__`) : document.getElementById(`${e.id}`);
                if (!el) {
                    throw new SystemException(`Nie znaleziono pola o id: ${eId} dla indeksu: ${repeatableSectionRowIdx}`);
                }

                if (isRepeatable) {
                    if (!repeatableSectionRowIdx) {
                        throw new SystemException(`Brak indeksu dla sekcji powtarzalnej od id: ${repeatableSectionId}`);
                    }

                    if (!repeatableSections[repeatableSectionId].hasOwnProperty(eId)) {
                        repeatableSections[repeatableSectionId][eId] = [];
                    }
                    repeatableSections[repeatableSectionId][eId].push({value: Input.getValue(el), meta: DocumentAttributeForm.collectMeta(el)})

                } else {
                    attributeData[eId] = {value: Input.getValue(el), meta: DocumentAttributeForm.collectMeta(el)};
                }
            });

        })(documentModel, 1);

        //todo: temporary - for test case. Move to whole document save procedure.
        if (typeof callback === 'function') {
            callback(attributeData);
        }
        attributeData['__REPEATABLE_SECTIONS'] = repeatableSections;

        return attributeData;
    }
}

export default DocumentAttributeForm;
