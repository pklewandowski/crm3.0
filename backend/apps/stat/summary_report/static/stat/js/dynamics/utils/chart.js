function create(chartCanvas, displayValues) {
    return new Chart(chartCanvas, {
        type: 'line',
        data: {
            labels: [],
            datasets: []
        },
        options: {
            hover: {
                "animationDuration": 0
            },
            // legend: {
            //     display: false
            // },
            tooltips: {
                enabled: true,
                callbacks: {
                    label: function (tooltipItem, data) {
                        return tooltipItem.yLabel.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1 ');
                    }
                }
            },
            animation: {
                duration: 1,
                onComplete: function () {
                    if (!displayValues) {
                        return;
                    }
                    let _this = this;
                    let ctx = this.chart.ctx;

                    ctx.font = Chart.helpers.fontString(
                        Chart.defaults.global.defaultFontSize,
                        Chart.defaults.global.defaultFontStyle,
                        Chart.defaults.global.defaultFontFamily
                    );
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'bottom';
                    ctx.fillStyle = '#666';

                    this.data.datasets.forEach(function (dataset, i) {

                        let meta = _this.chart.controller.getDatasetMeta(i);
                        meta.data.forEach(function (bar, index) {
                            let data = dataset.data[index];
                            ctx.fillText(data, bar._model.x, bar._model.y - 5);
                        });
                    })
                }
            },
            responsive: true,
            scales: {
                xAxes: [{
                    ticks: {
                        display: true,
                        precision: 0
                    }
                }],
                yAxes: [{
                    ticks: {
                        beginAtZero: true,
                        callback: function (label, index, labels) {
                            return label.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1 ');
                        }
                    }
                }]
            }
        }
    });
}

export {create};
