import IMask from "imask";

const INPUT_TYPES = ['text', 'password', 'number', 'email', 'tel', 'url', 'search', 'date', 'datetime', 'datetime-local', 'time', 'month', 'week'];
const classname = 'Input';

class Input {
    static setAttribute(el, attr) {
        if (!el) {
            return;
        }
        if (!attr) {
            return;
        }
        if (Array.isArray(attr)) {
            attr.forEach((prop) => {
                el.setAttribute(prop.name, prop.value);
            });
        } else {
            el.setAttribute(attr.name, attr.value);
        }
    }

    static setValue(el, val, current_value = true) {
        if (!el) {
            jsUtils.LogUtils.log(`[${classname}]: element is null`);
            return;
        }

        if (el.datepicker) {
            el.datepicker.setDate(val, {quiet: true});
            el.value = val;
            return;
        }

        if (!el.dataset?.current_value) {
            el.dataset.current_value = '';
        }

        current_value ? el.dataset.current_value = val : el.dataset.current_value = '';

        if (!Input.isNullValue(val) && el?.dataset?.autocomplete_url) { // for select2 autocomplete {text:..., val:...}
            let promise = ajaxCall({
                    method: 'get',
                    url: el.dataset.autocomplete_url,
                    data: {id: val}
                },
                (resp) => {
                    if (resp?.results?.length) {
                        let opt = new Option(resp.results[0].text, resp.results[0].id, true, true);
                        el.appendChild(opt);
                        el.value = resp.results[0].id;
                    }
                },
                (resp) => {
                    jsUtils.LogUtils.log(resp.responseJSON);
                },
            );
            window.documentAttributeDataPromises.push(promise);
        }

        if (el?.dataset['datatype'] === 'balance') {
            return JSON.parse(val).slider;
        }

        if (el.dataset['datatype'] === 'text' && _g.document.editors && _g.document.editors[el.id]) {
            return _g.document.editors[el.id].setData(val);
        }


        let value = null;

        if (val && el.dataset && el.dataset.subtype && el.dataset.subtype === 'percent') {
            value = (val * 100).toFixed(Input.isNumber(el.dataset.decimalplaces) ? el.dataset.decimalplaces : 2);
        } else {
            value = val;
        }

        if (el.type === 'checkbox') {
            el.checked = (value == 'T');

        } else if (el.imask) {
            el.imask.typedValue = Input.isNullValue(value) ? '' : value;
            el.imask.updateValue();

        } else {
            el.value = value;
        }
    }

    static setMask(el, type) {
        let maskData = null;

        if (type === 'currency') {
            maskData = {
                mask: Number,
                lazy: false,
                placeholderChar: '_',
                thousandsSeparator: ' ',
                normalizeZeros: true,
                padFractionalZeros: true
            };
        }

        if (type === 'percent') {
            maskData = {
                mask: Number,
                scale: 2,
                lazy: false,
                placeholderChar: '_',
                thousandsSeparator: ' ',
                normalizeZeros: true,
                padFractionalZeros: true
            };
        }

        if (maskData) {
            el.imask = IMask(el, maskData);
            return el.imask;
        }
        return null;
    }

    static unmaskValue(el) {
        if (el.imask) {
            return el.imask.unmaskedValue;
        } else {
            return el.value;
        }
    }

    static getValue(el, defaultValue = null) {
        if (!el) {
            return defaultValue;
        }

        let value = null;

        if (el.type === 'file') {
            return el.files[0];
        }

        // if item type is SELECT so don't need to unmask
        if (!el.nodeName) {
            console.log('no nodeName:', el);
        }
        if (el.nodeName.toUpperCase() === 'SELECT') {
            return el.value;
        }

        if (el.dataset && el.dataset['datatype'] === 'balance') {
            return JSON.stringify({
                slider: Input.unmaskValue(el),
                percentLeft: Input.unmaskValue(Input.getByCode(`${el.id}_pl`)),
                left: Input.unmaskValue(Input.getByCode(`${el.id}_l`)),
                right: Input.unmaskValue(Input.getByCode(`${el.id}_r`)),
                percentRight: Input.unmaskValue(Input.getByCode(`${el.id}_pr`))
            });
        }

        if (el.dataset['datatype'] === 'text' && _g.document.editors && _g.document.editors[el.id]) {
            return _g.document.editors[el.id].getData();
        }

        if (el.type === 'checkbox') {
            return el.checked ? 'T' : 'N';
        }

        value = Input.unmaskValue(el);

        if (!this.isNullValue(value)) {
            //if percent then divide by 100
            if (el.dataset.subtype === 'percent') {
                value = parseFloat((value / 100).toFixed(4));
            } else if (el.dataset.type === 'decimal') {
                value = parseFloat(value.toFixed(2));
            }

        } else if (!Input.isNullValue(defaultValue)) {
            return defaultValue;
        }
        return value;
    }

    static revertValue(el) {
        let val = el.dataset['current_value'];
        if (!val) {
            val = null;
        }
        el.value = val;
    }

    static empty(el) {
        el.value = '';
    }

    static isNumber(n) {
        return !isNaN(parseFloat(n)) && isFinite(n);
    }

    static coalesce(n, v) {
        return isNumber(n) ? n : v;
    }

    static get(selector) {
        return document.querySelector(selector);
    }

    static getByCode(code) {
        if (!code) {
            return null;
        }
        return Input.get(`[data-code="${code}"]`);
    }

    static getByName(name) {
        return Input.get(`[name="${name}"]`);
    }

    static getById(id) {
        return document.getElementById(id);
    }

    /*
    function check whether field label is truncated or not (long label truncat...)
     */
    static isTruncated(inputLabel) {
        let e = inputLabel;
        let c = Object.assign({}, e);
        c.style.cssText = 'display: "inline", width: "auto", visibility: "hidden"';
        document.appendChild(c);
        let cWidth = c.offsetWidth;
        c.remove();

        return (cWidth > e.offsetWidth);
    }

    static isNullValue(value) {
        return value == null || typeof value == 'undefined' || value === '';
    }

    static _setMinMax(el, min, max) {
        if (min) {
            el.imask.min = min;
        }

        if (max) {
            el.imask.max = max;
        }
    }

    static setIntegerMask(el, min, max) {
        el.imask = IMask(el,
            {
                mask: Number,
                scale: 0,
                lazy: false,
                thousandsSeparator: ' '
            });
        Input._setMinMax(el, min, max);
    }

    static setCurrencyMask(el, min, max) {
        el.imask = IMask(el,
            {
                mask: Number,
                scale: 2,
                lazy: false,
                thousandsSeparator: ' ',
                normalizeZeros: true,
                padFractionalZeros: true
            });
        Input._setMinMax(el, min, max);
    }
}

export default Input;
