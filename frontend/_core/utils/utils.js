import HtmlUtils from "./html-utils";
import {SystemException} from "../exception";

const className = 'Utils';

class Utils {
    static domElement(type, id, classList, callback = null, value = null, innerHTML = null, innerText = null) {
        let el = document.createElement(type);
        if (id) {
            el.id = id;
        }
        if (classList) {
            if (typeof classList === 'object') {
                el.classList.add(...classList);
            } else if (typeof classList === 'string') {
                el.classList.add(classList);
            }
        }
        if (value) {
            el.value = HtmlUtils.escapeScriptTag(value);
        }
        if (innerHTML) {
            el.innerHTML = HtmlUtils.escapeScriptTag(innerHTML);

        } else if (innerText) {
            el.innerHTML = HtmlUtils.escapeScriptTag(innerText);
        }
        return el;
    }

    static createElement(tagName, attrs = {}, ...children) {
      let dataset = [];
        if (attrs?.data) {
            for (let [key, val] of Object.entries(attrs.data)) {
                let d = {};
                d[key]=val;
                dataset.push(d);
            }
            attrs.data = null;
        }
        const elem = Object.assign(document.createElement(tagName), attrs);
        for(let i of dataset) {
            elem.dataset[Object.keys(i)[0]] = Object.values(i)[0];
        }

        for (const child of children) {
            if (Array.isArray(child)) elem.append(...child);
            else elem.append(child);
        }
        return elem;
    }

    // static appendChild(parent, child){
    //     if (Array.isArray(child))
    //         child.forEach((nestedChild) => appendChild(parent, nestedChild))
    //     else
    //         parent.appendChild(
    //             child.nodeType ? child : document.createTextNode(child)
    //         )
    // };
    //
    // static createElement(tag, props, ...children) {
    //     const element = document.createElement(tag);
    //
    //     Object.entries(props || {}).forEach(([name, value]) => {
    //         if (name.startsWith('on') && name.toLowerCase() in window)
    //             element.addEventListener(name.toLowerCase().substr(2), value);
    //         else element.setAttribute(name, value.toString())
    //     });
    //
    //     children.forEach((child) => {
    //         Utils.appendChild(element, child);
    //     });
    //
    //     return element;
    // }

    static isDomElement(el) {
        return el instanceof Element;
    }

    static toggleClass(e, className) {
        if (!e || !className) {
            jsUtils.LogUtils.log(`[${className}][toggleClass]: element or className not provided!`);
            return;
        }

        if (Array.from(e.classList).includes(className)) {
            e.classList.remove(className)
        } else {
            e.classList.add(className)
        }
    }

    static position(el) {
        let _rc = el.getBoundingClientRect();
        let rc = {};
        if (_rc) {
            // let bodyRc = document.body.getBoundingClientRect();
            rc.top = _rc.top;
            rc.left = _rc.left;
            rc.width = _rc.width;
            rc.height = _rc.height;
        }
        return rc;
    }

    static indicateChanged(e) {
        if (e.classList.contains('has-changed')) {
            e.classList.remove('has-changed');
            void e.offsetWidth; // needed for make make animation restart effective. Without it class switch does not take effect
        }
        e.classList.add('has-changed');
    }

    static nullValue(val, valIfNull = '') {
        if (!val) {
            return valIfNull;
        }
        return val;
    }

    static setContainer(container, className) {
        let _container = null;
        if (!container) {
            throw new SystemException(`[${className}]: no container provided`);
        }
        _container = Utils.isDomElement(container) ? container : document.getElementById(container);

        if (!_container) {
            throw new SystemException(`[${className}]: couldn't find container provided`);
        }

        return _container;
    }
}

export default Utils;