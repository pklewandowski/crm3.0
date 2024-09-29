import {BaseChart} from "../base-chart";

const type = 'doughnut';

class DoughnutChart extends BaseChart {
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

export {DoughnutChart};