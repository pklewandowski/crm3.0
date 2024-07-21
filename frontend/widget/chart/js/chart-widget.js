import "../scss/chart-widget.scss";
import {SystemException} from "../../../_core/exception";
import {BaseWidget} from "../../_core/widget-base";

const className = 'ChartWidget';

class ChartWidget extends BaseWidget {
    constructor(container, name, type) {
        super(container, name);
        this.type = type;
    }

    render() {

    }
}

export {ChartWidget}