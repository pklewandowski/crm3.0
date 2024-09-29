import HtmlUtils from "../../../../_core/utils/html-utils";
import {SystemException} from "../../../../_core/exception";

const className = 'Column';

class Column {

    static render(at, callback = null, opt = null) {
        let cl = document.createElement('div');
        cl.dataset['id'] = at.id;
        if (at.name || _g.document.mode === 'DEFINITION') {
            let panel = document.createElement('div');
            cl.appendChild(panel);
            panel.classList.add('heading-title');

            let span = document.createElement('div');
            span.classList.add('heading-title-text');
            panel.appendChild(span);
            span.innerHTML = HtmlUtils.escapeScriptTag(at.name);
            if (_g.document.mode === 'DEFINITION') {
                span.contentEditable = true;

                let handle = document.createElement('div');
                handle.classList.add(...['handle-column', 'handle-icon']);
                let i = document.createElement('i');
                i.classList.add(...['fa', 'fa-arrows-h']);
                handle.appendChild(i);
                cl.appendChild(handle);
            }
        }

        if (at.feature && at.feature.width) {
            cl.classList.add(...[`col-lg-${at.feature.width}`, 'column-container']);
        } else {
            throw new SystemException(`[${className}][_renderColumn]: attribute [id: ${at.id}]: feature.width variable not set`);
        }
        if (at.css_class) {
            cl.classList.add(at.css_class);
        }

        if (at.feature && at.feature.style) {
            cl.style.cssText = at.feature.style;
        }

        if (callback && callback.fn && typeof callback.fn === 'function') {
            callback.fn(cl, callback.opt);
        }

        return cl;
    }

    static width(column, width) {
        const prefix = "col-lg-";
        // this if fixes nulls and undefined-s cause (null == undefined) => true (but (null === undefined) => false)
        if (width == null) {
            let w = Array.from(column.classList).filter(c => c.startsWith(prefix))[0];
            if (w.length) {
                let res = w.substr(w.lastIndexOf('-') + 1, w.length);
                if (Input.isNumber(res)) {
                    return parseInt(res);
                } else {
                    throw new SystemException(`[${className}][changeWidth] the class with ${prefix} prefix has not number at the end. Instead is: ${res}`);
                }
            } else {
                return null;
            }
        } else if (!Input.isNumber(width)) {
            throw new SystemException(`[${className}][changeWidth] with is not a number: ${width}`);
        } else if (width < 1 || width > 12) {
            throw new SystemException(`[${className}][changeWidth] with must be in range <1:12>. Is: ${width}`);
        }

        let classes = Array.from(column.classList).filter(c => !c.startsWith(prefix));
        classes.push(`col-lg-${width}`);
        column.className = '';
        column.classList.add(...classes);
    }
}

export default Column;
