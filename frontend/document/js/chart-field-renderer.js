import Chart from 'chart.js';

class ChartFieldRenderer {
    constructor(type, title) {
        /**
         * chart types: line, bar, radar, pie, polar, polarArea, bubble, scatter
         */
        this.type = type;
        this.title = title;
        this.labels = [];
        this.className = 'ChartFieldRenderer';
        this.chart = null;
        this.ctx = document.createElement('canvas');
        this.isSetUp = false;

        this.init();
    }

    initDatasets() {
        this.datasets = [
            {
                label: '',
                data: [],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
                borderWidth: 2
            },
            // {
            //     // optional average dataset
            //     label: '',
            //     data: [3, 3, 3, 3, 3, 3],
            //     // Changes this dataset to become a line
            //     type: 'radar'
            // }
        ]
    }

    init() {
        this.initDatasets();
    }


    setUp(ds) {
        if (this.isSetUp) {
            return;
        }

        ds.map(e => {
            this.labels.push(e.name);
            let el = document.getElementById(e.id.toString());

            if (el) {
                this.datasets[0].data.push(Input.getValue(el) ? parseFloat(Input.getValue(el)) : '');
                el.addEventListener('change', () => {
                    this.update(ds)
                });
            } else {
                jsUtils.LogUtils.log(`[${this.className}][setUp] dataset element not found!`, null);
            }
        });

        this.isSetUp = true;
    }

    update(ds) {
        let data = [];
        ds.map(e => {

            let el = document.getElementById(e.id.toString());

            if (el) {
                data.push(Input.getValue(el) ? parseFloat(Input.getValue(el)) : null);
            } else {
                console.log(`[${this.className}][addDatasourceListeners] dataset element not found!`);
            }

            this.chart.data.datasets[0].data = data;
            this.chart.update();
        });
    }

    render() {
        this.chart = new Chart(this.ctx, {
            type: this.type,
            data: {
                labels: this.labels,
                datasets: this.datasets
            },
            options: {
                tooltips: {
                    displayColors:false,
                    callbacks: {
                        title: function (tooltipItems, data) {
                            return '';
                        },
                        label: function (tooltipItem, data) {
                            // let datasetLabel = '';
                            // let label = data.labels[tooltipItem.index];

                            return data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index];
                        }
                    }
                },
                legend: {
                    display: false
                },
                scale: {
                    angleLines: {
                        display: true
                    },
                    ticks: {
                        beginAtZero: true,
                        max: 5,
                        min: 0,
                        suggestedMax: 5,
                        stepSize: 1
                    }
                }
                // scales: {
                //     xAxes: [{
                //         ticks: {
                //             beginAtZero: true
                //         }
                //     }]
                // }
                // animation: {
                //     duration: 0,
                //     onComplete: function () {
                //         // render the value of the chart above the bar
                //         var ctx = this.chart.ctx;
                //         ctx.font = Chart.helpers.fontString(Chart.defaults.global.defaultFontSize, 'normal', Chart.defaults.global.defaultFontFamily);
                //         ctx.fillStyle = this.chart.config.options.defaultFontColor;
                //         ctx.textAlign = 'center';
                //         ctx.textBaseline = 'bottom';
                //         this.data.datasets.forEach(function (dataset) {
                //             for (var i = 0; i < dataset.data.length; i++) {
                //                 var model = dataset._meta[Object.keys(dataset._meta)[0]].data[i]._model;
                //                 ctx.fillText(dataset.data[i], model.x, model.y - 5);
                //             }
                //         });
                //     }
                // }
            },
            // showTooltips: false,

            // onComplete: function () {
            //
            //
            //     var ctx = this.chart.ctx;
            //     ctx.font = this.scale.font;
            //     ctx.fillStyle = this.scale.textColor;
            //     ctx.textAlign = "center";
            //     ctx.textBaseline = "bottom";
            //
            //     this.datasets.forEach(function (dataset) {
            //         dataset.points.forEach(function (points) {
            //             ctx.fillText(points.value, points.x, points.y - 10);
            //         });
            //     })
            // }
        });
    }
}

export default ChartFieldRenderer;