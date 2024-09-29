import {BaseChart} from "../base-chart";

const type = 'pie';

class PieChart extends BaseChart {
    constructor(container, data, options) {
        super(container, data, options);
    }

    validate() {
        return true;
    }

    render() {
        super.render(type);
    }
}

export {PieChart};