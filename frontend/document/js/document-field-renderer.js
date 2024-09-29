import IMask from 'imask';

import {setSelect2 as setAdvancedSelect2Feature} from "../../_core/autocomplete";
import HtmlUtils from "../../_core/utils/html-utils";
import {SystemException} from "../../_core/exception";
import ChartFieldRenderer from "./chart-field-renderer";
import {TOOLBAR_BTN, ToolbarUtils} from "../../_core/utils/toolbar-utils";
import BalanceControl from "../../_core/controls/balance-control/balance-control";

import {Datepicker} from "../../_core/controls/vanillajs-datepicker-3ws";
import pl from "../../_core/controls/vanillajs-datepicker-3ws/js/i18n/locales/pl";

pl.pl.daysMin = ["Nd", "Pn", "Wt", "Śr", "Cz", "Pt", "So"];
Object.assign(Datepicker.locales, pl);

const className = 'FieldRenderer';
const nullbooleanLovData = {
    "data": [{"lov_label": "Tak", "lov_value": "T", "lov_description": ""},
        {"lov_label": "Nie", "lov_value": "N", "lov_description": ""}], "nullvalue": true
};

class FieldRenderer {
    static _getFieldContainer(at) {

        let container = document.createElement('div');
        // if hidden input, there's no need to render any styled containers
        if (at?.attribute?.generic_datatype === 'hidden') {
            container.style.position = 'relative';
            return container;
        }

        container.classList.add('form-group');
        if ((at?.feature?.actionBtn) || at.name_icon) {
            let inputGroup = document.createElement('div');
            inputGroup.classList.add('input-group');
            container.appendChild(inputGroup);
        }
        return container;
    }

    static _renderLov(lov, options) {
        if (lov.nullvalue) {
            options.push(new Option("", ""));
            //options.push(new Option());
        }
        lov.data.map(opt => {
            let o = document.createElement('option');
            o.value = opt.lov_value;
            o.text = opt.lov_label;
            options.push(o);
            // return options;
        });
    }

    static handleDependencies(el) {

    }

    static _showValueList(at, el) {
        let vlcId = `valueList-${el.id}`;
        let vlc = document.getElementById(vlcId);

        if (!vlc) {
            vlc = jsUtils.Utils.domElement('div', vlcId, ['value-list-container', 'dropdown-layer']);
            let vlu = jsUtils.Utils.domElement('ul', null, 'value-list');
            vlc.appendChild(vlu);

            for (let i of JSON.parse(el.dataset['valuelist'])) {
                let vli = jsUtils.Utils.domElement('li', null, 'value-list-item');
                vli.innerHTML = i;
                vli.addEventListener('click', () => {
                    el.value = i;
                    vlc.style.display = 'none';
                });
                vlu.appendChild(vli);
            }
            document.body.appendChild(vlc);
        }

        let pos = jsUtils.Utils.position(el);
        vlc.style.left = `${Math.floor(pos.left + 2)}px`;
        vlc.style.top = `${Math.floor(pos.top + pos.height - 1)}px`;
        vlc.style.width = `${pos.width + 3}px`;
        vlc.style.display = 'block';
    }

    static _setFeatures(at, el, value) {
        if (at.feature) {
            if (at.feature.dataset) {
                at.feature.dataset.map((e) => {
                    el.dataset[Object.keys(e)[0]] = Object.values(e)[0];
                });
            }
            if (at.feature.multiple) {
                el.setAttribute('multiple', true);
            }

            if (at.feature.dynamicLov) {
                FieldRenderer.renderDynamicLov(el, at.feature.dynamicLov, value);
                return;
            }


            if (!window.documentDefinitionMode) {
                if (at.feature.autocomplete) {
                    setAdvancedSelect2Feature($(el));

                } else if (at.feature.autocomplete_url) {
                    el.dataset['autocomplete_url'] = at.feature.autocomplete_url;
                    setAdvancedSelect2Feature($(el), true, at.feature.autocomplete_add_query ? at.feature.autocomplete_add_query : null);
                }
            }

            if (at.feature.calculable) {
                if (!at.feature.calculable?.editable) {
                    el.readOnly = true;
                    el.placeholder = at.placeholder ? at.placeholder : 'pole wyliczalne';
                }
            }

            if (at.feature.valueList) {
                el.dataset['valuelist'] = JSON.stringify(at.feature.valueList);
                el.addEventListener('click', (e) => {
                    FieldRenderer._showValueList(at, e.target);
                });
            }

            // add action event listeners to the fields
            // todo: if an item or item being modified by action is not editable, raise error that it cannot be modified
            // todo: to do this set onchange raising error on read only item. Wrap then action function to revert changes
            if (at.feature.actions) {
                // listener action
                if (at.feature.actions.listener) {
                    eval(at.feature.actions.listener.fn);
                }
                // change action
                if (at.feature.actions.change) {
                    if (at.feature.autocomplete_url) {
                        $(el).on('select2:select', (e) => {
                            eval(at.feature.actions.change.fn)(e);
                        });
                    }
                    el.addEventListener('change', (e) => {
                        eval(at.feature.actions.change.fn)(e);
                    });
                }
            }
        }

        // add mask placeholder
        {
            let mask = null;

            if (at.feature && at.feature.mask) {
                mask = at.feature.mask;
            } else if (at.attribute.mask) {
                mask = at.attribute.mask;
            }
            if (mask) {
                el.imask = IMask(el, {
                    mask: mask,
                    lazy: false,
                    placeholderChar: '_'
                });
            } else {
                switch (at.attribute.generic_datatype) {
                    case  'decimal':
                    case 'currency':
                        let maskData = {
                            mask: Number,
                            lazy: false,
                            placeholderChar: '_',
                            thousandsSeparator: ' ',
                            normalizeZeros: true,
                            padFractionalZeros: true
                        };

                        // set decimal places
                        if (at.feature && at.feature.decimalPlaces != null) {
                            maskData['scale'] = parseInt(at.feature.decimalPlaces);
                        } else if (at.attribute.decimal_places != null) {
                            maskData['scale'] = parseInt(at.attribute.decimal_places);
                        } else {
                            maskData['scale'] = 2;
                        }

                        if (maskData['scale'] === 0) {
                            maskData['padFractionalZeros'] = false;
                        }

                        // set min and max values
                        if (at?.feature?.minValue) {
                            maskData['min'] = parseFloat(at.feature.minValue);

                        } else if (at.attribute.min_value) {
                            maskData['min'] = parseFloat(at.attribute.min_value);
                        }

                        if (at?.feature?.maxValue) {
                            maskData['max'] = parseFloat(at.feature.maxValue);
                        } else if (at.attribute.max_value) {
                            maskData['max'] = parseFloat(at.attribute.max_value);
                        }

                        el.imask = IMask(el, maskData);
                        el.style.textAlign = 'right';
                        break;

                    default:
                        break;
                }
            }
        } // end add mask placeholder
    }

    static _setDependency(el, resetValue = true) {
        let selector = '.row';

        if (!el.closest(selector)) {
            return;
        }

        for (const [k, v] of Object.entries(el.dependency)) {
            let i = el.closest(selector).querySelector(`[data-code="${k}"]`);
            if (!i.dependentOn) {
                i.dependentOn = el.dataset['code'];
                i.dependentOnId = el.id;
            }

            if (v.includes(el.value)) {
                i.closest('.form-group').style.display = 'inherit';

            } else {
                if (resetValue) {
                    i.value = '';
                }
                i.closest('.form-group').style.display = 'none';
            }
        }
    }

    static _setDependencies(el, resetValue = true) {
        el.addEventListener('change', () => {
            FieldRenderer._setDependency(el, resetValue);
        });

        // todo: DRUT!!! set document event as global dict structure cand get it from this dict
        document.addEventListener('documentAttributeEvt:documentCreated', () => {
            FieldRenderer._setDependency(el, resetValue);
        });

        document.addEventListener(window.evtRepeatableSectionCreated.type, () => {
            FieldRenderer._setDependency(el, resetValue);
        });


        // ********************** DO NOT DELETE FOR NOW ************************************
        //** the another approach - dependency is specified on dependent items not on dependor :)

        // for (let i of Array.from(
        //     el.closest('.row-container').querySelector(`[data-code="${at.id}"]`))) {
        //
        //     if (i.dependency && i.dependency[el.dataset['id']]) {
        //         if (i.dependency[el.dataset['id']].includes(el.value)) {
        //             i.closest('.form-group').style.display = 'inherit';
        //         } else {
        //             if (resetValue) {
        //                 i.value = '';
        //             }
        //             i.closest('.form-group').style.display = 'none';
        //         }
        //     }
        // }
        // });
    }

    static _addActionBtn(fieldContainer, el, label = null) {
        // ads action button to field container
        let ig = fieldContainer.getElementsByClassName('input-group')[0];
        ig.appendChild(el);
        if (label) {
            ig.appendChild(label);
        }
        let span = document.createElement('span');
        span.classList.add('input-group-btn');

        let actionBtn = document.createElement('button');
        actionBtn.classList.add(...['btn', 'btn-default', 'action-btn']);
        actionBtn.textContent = 'go!';
        actionBtn.type = 'button';

        span.appendChild(actionBtn);
        ig.appendChild(span);
    }

    static _addNameIcon(at, fieldContainer, el, label = null) {
        let ig = fieldContainer.getElementsByClassName('input-group')[0];
        ig.appendChild(el);
        if (label) {
            ig.appendChild(label);
        }

        let span = document.createElement('span');
        span.classList.add('input-group-addon');
        let i = jsUtils.Utils.domElement('i', null, at.name_icon);

        span.appendChild(i);
        ig.appendChild(span);
    }

    /**
     * function showCalculableSources:
     *  On mouse-down / mouse-up on given calculable fields' label highlights / unhighlights the fields that are the sources for given calculable fields
     * @param sources - array including ids of source fields
     * @param show - boolean Toggle highlighting, true: highlight , false: unhighlight
     */
    static showCalculableSources(sources, show) {
        if (!Array.isArray(sources)) {
            throw SystemException(`[${className}][showCalculableSources]: Sources must be an array`);
        }

        sources.map(e => {
            let el = Input.getByCode(e.toString());
            if (!el) {
                throw SystemException(`[${className}][showCalculableSources]: Couldn't find element with id: ${e}`);
            }
            let fGroup = el.closest('.form-group');
            if (!fGroup) {
                return;
            }
            if (show) {
                fGroup.classList.add('show-source');
            } else {
                fGroup.classList.remove('show-source');
            }
        });
    }

    /**
     * Function renderLabel
     * Renders the label of the field. If @showCalculable=true, then on label click function showCalculableSources is executed
     * @param at
     * @param label
     * @param showCalculable
     * @returns {HTMLLabelElement}
     */
    static renderLabel(at, label, showCalculable) {
        if (at.attribute?.generic_datatype === 'hidden') {
            return;
        }
        let lbl = document.createElement('label');
        lbl.htmlFor = at.id;
        if (at.description) {
            lbl.dataset['toggle'] = 'tooltip';
            lbl.dataset['html'] = 'true';
            lbl.title = at.description;
            $(lbl).tooltip({container: 'body'});
        }
        lbl.innerHTML = label ? HtmlUtils.escapeScriptTag(label) : at.label ? HtmlUtils.escapeScriptTag(at.label) : HtmlUtils.escapeScriptTag(at.name);
        if (showCalculable && at.feature && at.feature.calculable) {
            lbl.addEventListener("mousedown", () => {
                FieldRenderer.showCalculableSources(at.feature.calculable.sources, true)
            });
            lbl.addEventListener("mouseup", () => {
                FieldRenderer.showCalculableSources(at.feature.calculable.sources, false)
            });
        }
        return lbl;
    }

    static renderDynamicLov(el, dynamicLovOptions, value) {
        function render(resp) {
            if (dynamicLovOptions.nullvalue) {
                el.appendChild(new Option('', ''));
            }
            for (let i of resp) {
                let opt = new Option(i.label, i.value, '', value == i.value);
                if (i.data) {
                    for (let d of i.data) {
                        opt.dataset[d.name] = d.value;
                    }
                }
                el.appendChild(opt);
            }
        }

        if (!window.documentDefinitionMode) {
            let promise = ajaxCall({
                    method: 'get',
                    url: dynamicLovOptions.url
                },
                (resp) => {
                    render(resp);
                },
                (resp) => {
                    jsUtils.LogUtils.log(resp.responseJSON)
                }
            );
            window.documentAttributeDataPromises.push(promise);
        }
    }

    static getTagName(at, options) {
        let tagName = null;

        if (at.lov?.data) {
            tagName = 'select';
            FieldRenderer._renderLov(at.lov, options);

        } else if (at.feature?.autocomplete_url || at?.feature?.dynamicLov) {
            tagName = 'select';

        } else {
            if (!at.attribute?.generic_datatype) {
                throw SystemException(`[${className}][renderField][getTagName]: field attribute generic data type not defined!`);
            }

            // tagName takes two part field description 'name.type' variable. If no type then only 'name.' part is expressed with following dot.
            switch (at.attribute?.generic_datatype) {

                case 'text':
                    tagName = 'textarea';
                    break;

                case 'hidden':
                    tagName = 'input.hidden';
                    break;

                case 'string':

                    tagName = 'input.text';

                    break;

                case 'date':
                    tagName = 'input.text.date';
                    break;

                case 'boolean':
                    tagName = 'input.checkbox';
                    break;

                case 'nullboolean':
                    tagName = 'select';
                    FieldRenderer._renderLov(nullbooleanLovData, options);
                    break;

                case 'title':
                    tagName = 'span';
                    break;

                case 'separator':
                    tagName = 'separator';
                    break;

                case 'chart':
                    tagName = 'chart';
                    break;

                case 'balance':
                    tagName = 'balance';
                    break;

                default:
                    tagName = 'input.text';
                    break;
            }
        }
        return tagName;
    }

    static handleSpecialFields(at, tagName, data) {
        switch (tagName) {
            case 'separator':
                if (_g.document.mode && _g.document.mode === 'DEFINITION') {
                    let cnt = jsUtils.Utils.domElement('div', null);
                    cnt.style.position = 'relative';

                    let handle = ToolbarUtils.handleBtn(TOOLBAR_BTN.sm);

                    cnt.appendChild(jsUtils.Utils.domElement('hr', ''));
                    cnt.appendChild(handle);

                    return {fieldContainer: cnt};
                }

                let fieldContainer = FieldRenderer._getFieldContainer(at);
                let hr = jsUtils.Utils.domElement('hr', '');
                fieldContainer.appendChild(hr);
                hr.dataset['code'] = at.id;
                return {fieldContainer: fieldContainer};


            case 'chart':
                if (!at.feature || !at.feature.chart) {
                    throw new SystemException(`[addDatasourceListeners] Attribute has no chart defined: ${at.id}`);
                }
                if (!at.feature || !at.feature.chart.type) {
                    throw new SystemException(`[${this.className}][addDatasourceListeners] Attribute has no chart type defined`);
                }
                if (!at.feature || !at.feature.chart.dataset) {
                    throw new SystemException(`[${this.className}][addDatasourceListeners] Attribute has no chart dataset defined`);
                }

                if (!Array.isArray(at.feature.chart.dataset)) {
                    throw new SystemException(`[${this.className}][addDatasourceListeners] Attribute chart datraset must be an array`);
                }
                at.chart = new ChartFieldRenderer(at.feature.chart.type, at.name);
                return {fieldContainer: at.chart.ctx};

            case 'balance':
                return {fieldContainer: new BalanceControl(at, data ? data[at.id] : null).render()};

            default:
                return null;
        }
    }

    static _getDataValue(data, at, rIdx) {
        if (data && data[at.id] != null) {
            if (rIdx == null) {
                return {
                    value: data[at.id] ? data[at.id].value : null,
                    meta: data[at.id] ? data[at.id].meta : null
                };
            }
            if (Array.isArray(data[at.id])) {
                return data[at.id][rIdx] !== undefined ?
                    {
                        value: data[at.id][rIdx] ? data[at.id][rIdx].value : null,
                        meta: data[at.id][rIdx] ? data[at.id][rIdx].meta : null
                    } : {value: null, meta: null};
            }
            return {value: data[at.id] ? data[at.id].value : null, meta: data[at.id] ? data[at.id].meta : null}
        }
        return {value: null, meta: null};
    }

    /**
     * function render
     * Main render field function. Renders field with all its features like type, ccs, label and extra features defined in feature model data
     * @param at
     * @param data
     * @param rIdx
     * @param label
     * @param renderContainer
     * @param defaultValue
     * @param defaultLabel
     * @param callback
     * @param ver - Visible|Editable|Required
     *
     * @returns {{fieldContainer: HTMLElementTagNameMap[K]}|{fieldContainer: HTMLDivElement}|{fieldContainer: HTMLHRElement}}
     */
    static render(at,
                  data,
                  rIdx,
                  label = true,
                  renderContainer = true,
                  defaultValue = null,
                  defaultLabel = null,
                  callback = null,
                  ver = null
    ) {

        let _data = FieldRenderer._getDataValue(data, at, rIdx);
        let dataValue = _data.value;
        let dataMeta = _data.meta;

        dataValue = dataValue === undefined ? null : dataValue;
        dataMeta = dataMeta === undefined ? null : dataMeta;

        let fieldContainer;

        if (renderContainer) {
            // if fieldContainer then generate form-group like container for field
            fieldContainer = FieldRenderer._getFieldContainer(at);
        } else {
            fieldContainer = document.createElement('div');
            fieldContainer.style.position = 'relative';
        }
        let tagName;
        let options = [];
        let fieldCss = ['form-control', 'input-md'];

        if (at.css_class) {
            let cls = at.css_class.split(' ');
            cls.map(e => {
                fieldCss.push(e);
            });
        }

        if (at.selector_class) {
            fieldCss.push(at.selector_class);
        }

        tagName = FieldRenderer.getTagName(at, options);
        let specialField = FieldRenderer.handleSpecialFields(at, tagName, data);

        if (specialField) {
            return specialField;
        }

        let tagSplit = tagName.split(".");

        let el = document.createElement(tagSplit[0]);
        let elementType = tagSplit[1];

        if (typeof tagSplit[2] !== 'undefined') {
            switch (tagSplit[2]) {
                case 'date':
                    if (!window.documentDefinitionMode) {
                        fieldCss.push('date-field');


                        // todo: move it to separate function or update setDatePicker()

                        new Datepicker(el, {
                            autohide: true,
                            showOnClick: true,
                            language: 'pl',
                            format: 'yyyy-mm-dd',
                            orientation: 'bottom'
                        });
                        // workaround until unify calendar control: one for all items. Now we have two different calendars and need to move scheduler.schedule
                        // to vanillajs-datepicker-3ws calendar
                        el.minDate = function (minDate) {
                            el.datepicker.setOptions({minDate: minDate});
                        };
                        el.addEventListener('changeDate', () => {
                            el.dispatchEvent(new Event('change', {bubbles: true}));
                        });
                    }

                    // setDatePicker($(el));
                    break;
                default:
                    break;
            }
        }

        if (!window.documentDefinitionMode) {
            if (at?.feature?.style) {
                el.style.cssText = at.feature.style;
            }
        }

        if (elementType) {
            el.type = elementType;
        }

        // add code to element. Important for choosing sources for calculable fields and other staff
        el.dataset['code'] = at.code;
        el.dataset['name_short'] = at.name_short;
        el.dataset['name_icon'] = at.name_icon;

        //  set autocomplete off
        el.setAttribute("autocomplete", "off");

        // render the label
        let _label;
        if (label && (!Input.isNullValue(at.name) || defaultLabel)) {
            _label = FieldRenderer.renderLabel(at, defaultLabel, true)
        }

        if (at?.feature?.actionBtn) {
            FieldRenderer._addActionBtn(fieldContainer, el, _label);

        } else if (at.name_icon) {
            FieldRenderer._addNameIcon(at, fieldContainer, el, _label);

        } else {
            fieldContainer.appendChild(el);
            if (_label) {
                fieldContainer.appendChild(_label);
            }
        }

        // ending render element
        el.classList.add(...fieldCss);
        el.name = at.id;
        el.id = (rIdx != null) ? at.id.toString() + `__${rIdx}__` : at.id;
        el.dataset['id'] = at.id;
        el.dataset['datatype'] = at.attribute.generic_datatype;
        el.dataset['subtype'] = at.attribute.subtype ? at.attribute.subtype : '';
        el.dataset['decimalplaces'] = at.attribute.decimal_places;
        el.placeholder = at.placeholder ? at.placeholder : '';

        // if field is select, add defined options
        options.map(opt => {
            el.add(opt, null);
        });

        FieldRenderer._setFeatures(at, el, dataValue);

        if (at.dependency) {
            el.dependency = at.dependency;
            el.dataset['dependency'] = `${at.dependency}`;

            FieldRenderer._setDependencies(el);
        }

        // set value of normal (not async ajax query) field
        let val = dataValue;

        if (Input.isNullValue(val)) {
            if (defaultValue) {
                el.dataset['defaultValue'] = defaultValue;
                val = defaultValue;

            } else if (at.default_value) {
                el.dataset['defaultValue'] = at.default_value;
                val = at.default_value;
            }
        }

        Input.setValue(el, val);
        if (dataMeta) {
            for (let [key, value] of Object.entries(dataMeta)) {
                el.dataset[`__meta__${key}`] = value;
            }
        }


        // set readonly
        if (at.feature?.readonly) {
            el.setAttribute('disabled', 'disabled');
        } else {
            if (ver && Object.keys(ver).length) {
                if (!ver.e) {
                    el.setAttribute('disabled', 'disabled');
                }
                el.dataset['required'] = ver.r;
            }
        }

        if (_g?.document?.mode === 'DEFINITION') {
            let handle = ToolbarUtils.handleBtn(TOOLBAR_BTN.sm);
            fieldContainer.appendChild(handle);

        } else {
            // add default change action listener
            // this indicates that given element value was changed by user. Even after save this changed indicator is set to true.
            // it's information for some update procedures that require update only when field wasn't changed by user - ie. schedule instalment capital field
            el.hasChanged = false;
            el.changeHistory = [el.value];

            el.addEventListener('change', () => {
                el.hasChanged = true;
                el.changeHistory.push(el.value);
            });

            // set current value of the field to compare it th the new value when changed
            el.addEventListener('focus', () => {
                el.dataset.current_value = Input.getValue(el);
            });
        }

        return {fieldContainer: fieldContainer};
    }
}


export default FieldRenderer;
