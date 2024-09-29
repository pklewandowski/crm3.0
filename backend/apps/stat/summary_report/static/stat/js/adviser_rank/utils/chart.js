function create(amountCtx) {
    return new Chart(amountCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: []
        },
        options: {
            hover: {animationDuration: 1},
            legend: {display: true},
            tooltips: {enabled: false},
            animation: {
                duration: 1,
                onComplete: function () {
                    let _this = this;
                    let ctx = this.chart.ctx;

                    ctx.font = Chart.helpers.fontString(
                        11, //Chart.defaults.global.defaultFontSize,
                        Chart.defaults.global.defaultFontStyle,
                        Chart.defaults.global.defaultFontFamily
                    );
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'bottom';
                    ctx.fillStyle = '#ffffff';

                    this.data.datasets.forEach(function (dataset, i) {

                        let meta = _this.chart.controller.getDatasetMeta(i);
                        meta.data.forEach(function (bar, index) {
                            let data = dataset.data[index];
                            if (data > 0) {
                                ctx.fillText(
                                    data.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1 '),
                                    bar._model.x,
                                    bar._model.y + bar.height() / 2 + 8);
                            }
                        });
                    })
                }
            },
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                xAxes: [{
                    stacked: true,
                    ticks: {
                        display: true,
                        precision: 0
                    }
                }],
                yAxes: [{
                    display: true,
                    stacked: true,
                    ticks: {
                        beginAtZero: true,
                        callback: function (label, index, labels) {
                            return label.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1 ');
                        }
                    }
                }]
            },
            // onClick: function(event, arr) {
            //     console.log(arr);
            // }
        },
    });
}

export {create};