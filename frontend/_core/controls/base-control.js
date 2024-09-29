import {NotImplementedException} from "../exception";

class BaseControl {
    constructor(container, data, autoRender = true) {
        this.container = jsUtils.Utils.setContainer(container, this.constructor.name);
        this.data = data;
        this.autoRender = autoRender;
    }

    render() {
        throw new NotImplementedException();
    }

    getByName(name, many = false) {
        let selector = `[name="${name}"]`;
        if (many) {
            return this.container.querySelectorAll(selector)
        }
        return this.container.querySelector(selector)
    }
}

export {BaseControl}