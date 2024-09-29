import {BaseControl} from "../../base-control";
import {PieChart} from "../../../chart/js/chart-types/pie-chart";
import {DoughnutChart} from "../../../chart/js/chart-types/doughnut-chart";
import {BarChart} from "../../../chart/js/chart-types/bar-chart";


const className = 'ChartControl';

class ChartControl extends BaseControl {
    constructor(container, data, type, options) {
        super(container, data);
        this.type = type;
        this.options = options;
    }

    render() {
        // new PieChart(this.container, this.data, this.options).render();
        switch (this.type) {
            //     case 'line':
            //         new LineChart(this.container, this.data).render();
            //         break;
            case 'bar':
                new BarChart(this.container, this.data, this.options).render();
                 break;
            //     case 'radar':
            //         new RadarChart(this.container, this.data).render();
            //         break;
            case 'pie':
                new PieChart(this.container, this.data, this.options).render();
                break;
            case 'doughnut':
                new DoughnutChart(this.container, this.data, this.options).render();
                break;
            //     case 'bubble':
            //         new BubbleChart(this.container, this.data).render();
            //         break;
            //     case 'scatter':
            //         new ScatterChart(this.container, this.data).render();
            //         break;
            //     default:
            //         throw new SystemException(`[${className}]: chart type provided (${this.type}) is not supported`);
        }
    }
}

export {ChartControl};