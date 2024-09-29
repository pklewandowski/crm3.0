import {SystemException} from "../../../_core/exception";

import "../scss/number-widget.scss";
import {HomeInfoPanel} from "../../../home/js/home-info-panel";
import StringUtils from "../../../_core/utils/string-utils";

const className = 'NumberWidget';

class NumberWidget {
    constructor(container, name, value = null, url = null) {
        if (!container) {
            throw new SystemException(`[${className}]: no container provided`);
        }
        if (!name) {
            throw new SystemException(`[${className}]: no widget name provided`);
        }

        this.name = name;
        this.value = value;
        this.url = url;
        this.container = jsUtils.Utils.setContainer(container);

        this.infoPanel = new HomeInfoPanel(name);
        this.infoPanel.panel.classList.add('number-widget');
        this.valueContainer = <div className="number-widget-value"></div>;
        this.infoPanel.panelBody.appendChild(this.valueContainer);

        this.container.appendChild(this.infoPanel.panel);

        this.render();
    }

    setValue(value) {
        this.valueContainer.innerText = StringUtils.toProperTitleCase(value);
    }

    getValue() {
        ajaxCall({
            method: 'get',
            url: this.url
        }).then(
            (resp) => {
                setValue(resp.value);
            },
            (resp) => {
                throw new SystemException(resp.responseJSON);
            });
    }

    render() {
        this.url ? this.getValue() : this.setValue(this.value);
    }
}

export {NumberWidget}