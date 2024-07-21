import {NotImplementedException, SystemException} from "../../_core/exception";

const className = 'BaseWidget';

class BaseWidget {
    constructor(container, name) {
         if(!name) {
            throw new SystemException(`[${className}]: no widget name provided`);
        }
        this.container = jsUtils.Utils.setContainer(container, className);
        this.name = name;
    }

    render() {
        throw new NotImplementedException();
    }
}

export {BaseWidget};