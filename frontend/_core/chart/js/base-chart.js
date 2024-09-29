
import {NotImplementedException, SystemException} from "../../exception";
import Chart from "chart.js";

const className = 'BaseChart';

const defaults = {responsive: true,};

const bgColors = [
    'rgba(255, 99, 132, 1)',
    'rgba(54, 162, 235, 1)',
    'rgba(255, 206, 86, 1)',
    'rgba(75, 192, 192, 1)',
    'rgba(153, 102, 255, 1)',
    'rgba(255, 159, 64, 1)',
    'rgba(255, 99, 132, 1)',
    'rgba(54, 162, 235, 1)',
    'rgba(255, 206, 86, 1)',
    'rgba(75, 192, 192, 1)',
    'rgba(153, 102, 255, 1)',
    'rgba(255, 159, 64, 1)',
    'rgba(255, 99, 132, 1)',
    'rgba(54, 162, 235, 1)',
    'rgba(255, 206, 86, 1)',
    'rgba(75, 192, 192, 1)',
    'rgba(153, 102, 255, 1)',
    'rgba(255, 159, 64, 1)',
    'rgba(255, 99, 132, 1)',
    'rgba(54, 162, 235, 1)',
    'rgba(255, 206, 86, 1)',
    'rgba(75, 192, 192, 1)',
    'rgba(153, 102, 255, 1)',
    'rgba(255, 159, 64, 1)'
];


class BaseChart {

    constructor(container, data, options = null) {
        this.container = jsUtils.Utils.setContainer(container, className).querySelector('canvas');
        if (!this.container) {
            throw new SystemException(`[${className}]: couldn't find container canvas for chart object`);
        }
        if (!data) {
            throw new SystemException(`[${className}]: data must be provided as number array`);
        }
        this.data = {
            datasets: [],
            labels: [],
        };

        for (let i in data.data) {
            this.data.datasets.push({data: data.data[i], backgroundColor: options.bgColors ? options.bgColors : bgColors, label: ''});

            this.data.labels = data.labels;
        }

        this.options = Object.assign({}, defaults, options);
        this.chart = null;

        this.validate();
    }

    validate() {
        throw new NotImplementedException();
    }

    render(type) {
        this.chart = new Chart(
            this.container.getContext('2d'),
            {
                type: type,
                data: this.data,
                options: this.options
            });
        return this.chart;
    }
}

export {BaseChart};