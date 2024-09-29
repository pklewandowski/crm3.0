import * as chart from "./utils/chart.js";


const Dynamics = function (canvasContainer) {
    let brdColor = ['rgb(38,75,128)', 'rgb(128,49,36)', 'rgb(7,101,47)'];
    let bkgColor = ['rgba(38,75,128, .1)', 'rgba(128,49,36, .1)', 'rgba(7,101,47, .1)'];

    let cumulativeIncomeCountChartContainer = canvasContainer.find('#cumulativeIncomeCountChartContainer');
    let cumulativeIncomeAmountRequestedChartContainer = canvasContainer.find('#cumulativeIncomeAmountRequestedChartContainer');
    let cumulativeIncomeAmountGrantedChartContainer = canvasContainer.find('#cumulativeIncomeAmountGrantedChartContainer');

    this.cumulativeIncomeCountChart = null;
    this.cumulativeIncomeAmountRequestedChart = null;
    this.cumulativeIncomeAmountGrantedChart = null;

    let _this = this;

    this.clearDatasets = function () {

        this.cumulativeIncomeCountChart.data.datasets = [];
        this.cumulativeIncomeAmountRequestedChart.data.datasets = [];
        this.cumulativeIncomeAmountGrantedChart.data.datasets = [];

        this.cumulativeIncomeCountChart.data.labels = [];
        this.cumulativeIncomeAmountRequestedChart.data.labels = [];
        this.cumulativeIncomeAmountGrantedChart.data.labels = [];

    };

    this.fillLabels = function (chart) {
        for (let i = 1; i <= 31; i++) {
            this.cumulativeIncomeCountChart.data.labels.push(i);
            this.cumulativeIncomeAmountRequestedChart.data.labels.push(i);
            this.cumulativeIncomeAmountGrantedChart.data.labels.push(i);
        }
    };

    function addDataset(chart, label, data, bColorIndex) {
        chart.data.datasets.push(
            {
                label: label,
                data: data,
                borderColor: brdColor[bColorIndex],
                lineTension: 0,
                // fill: false,
                backgroundColor: bkgColor[bColorIndex],
                borderWidth: 1
            }
        )
    }

    this.createChart = function () {
        let cumulativeIncomeCountCtx = cumulativeIncomeCountChartContainer[0].getContext('2d');
        let cumulativeIncomeAmountRequestedCtx = cumulativeIncomeAmountRequestedChartContainer[0].getContext('2d');
        let cumulativeIncomeAmountGrantedCtx = cumulativeIncomeAmountGrantedChartContainer[0].getContext('2d');

        cumulativeIncomeCountCtx.clearRect(0, 0, cumulativeIncomeCountChartContainer[0].width, cumulativeIncomeCountChartContainer[0].height);
        cumulativeIncomeAmountRequestedCtx.clearRect(0, 0, cumulativeIncomeAmountRequestedChartContainer[0].width, cumulativeIncomeAmountRequestedChartContainer[0].height);
        cumulativeIncomeAmountGrantedCtx.clearRect(0, 0, cumulativeIncomeAmountGrantedChartContainer[0].width, cumulativeIncomeAmountGrantedChartContainer[0].height);

        if (this.cumulativeIncomeCountChart) {
            this.cumulativeIncomeCountChart.destroy();
        }
        this.cumulativeIncomeCountChart = chart.create(cumulativeIncomeCountCtx, true);

        if (this.cumulativeIncomeAmountRequestedChart) {
            this.cumulativeIncomeAmountRequestedChart.destroy();
        }
        this.cumulativeIncomeAmountRequestedChart = chart.create(cumulativeIncomeAmountRequestedCtx, false);

        if (this.cumulativeIncomeAmountGrantedChart) {
            this.cumulativeIncomeAmountGrantedChart.destroy();
        }
        this.cumulativeIncomeAmountGrantedChart = chart.create(cumulativeIncomeAmountGrantedCtx, false);
    };

    this.renderData = function (data) {
        this.clearDatasets();
        this.fillLabels();

        let bColorIndex = 0;

        $.each(data, function (_label, _data) {
            let dt_cnt = [];
            let dt_req = [];
            let dt_grt = [];
            for (let i in _data) {
                dt_cnt.push(_data[i].cnt);
                dt_req.push(_data[i].req);
                dt_grt.push(_data[i].grt);
            }
            addDataset(_this.cumulativeIncomeCountChart, _label, dt_cnt, bColorIndex);
            addDataset(_this.cumulativeIncomeAmountRequestedChart, _label, dt_req, bColorIndex);
            addDataset(_this.cumulativeIncomeAmountGrantedChart, _label, dt_grt, bColorIndex);
            bColorIndex++;
        });

        this.cumulativeIncomeCountChart.update();
        this.cumulativeIncomeAmountRequestedChart.update();
        this.cumulativeIncomeAmountGrantedChart.update();
    };


    this.collectData = function () {

    };

    function init() {
        _this.createChart();
    }

    init();
};

export default Dynamics;