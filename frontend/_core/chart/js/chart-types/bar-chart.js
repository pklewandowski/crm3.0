import {BaseChart} from "../base-chart";

const type = 'bar';

class BarChart extends BaseChart {
    constructor(container, data, options) {
        let opt = Object.assign({}, options, {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },

                legend: {
                    display: false,
                }

                // animation: {duration: 0},
                // hover: {animationDuration: 0},
                // responsiveAnimationDuration: 0
            }
        );

        super(container, data, opt);
    }

    validate() {
        return true;
    }

    render() {
        super.render(type);
    }
}

export {BarChart};