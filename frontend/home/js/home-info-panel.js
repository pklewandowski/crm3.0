import {InfoPanel} from "../../widget/_core/infoPanel/js/info-panel";

class HomeInfoPanel extends InfoPanel {
    constructor(title) {
        super(title);
        this.addClass(['home-info-panel']);
        this.addClass(['home-info-panel-body'], true);
    }
}

export {HomeInfoPanel};