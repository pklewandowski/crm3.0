import "../scss/styles.scss";
import {Panel} from "../../../../_core/containers/panel/js/panel";

const className = 'InfoPanel';

class InfoPanel extends Panel {
    constructor(title = '') {
        super(title);
        this.panel.classList.add('widget-info-panel');
        this.panelBody.classList.add('widget-info-panel-body');
    }
}

export {InfoPanel};