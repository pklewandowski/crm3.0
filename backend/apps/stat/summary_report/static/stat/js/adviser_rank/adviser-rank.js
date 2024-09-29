import * as chart from './utils/chart.js'
import {initialDatasets} from "./utils/datasets.js";

const AGR_TYPE = ['NEW', 'ANX', 'PRLG', 'UGD', 'XXX'];
const AdviserRank = function (canvasContainer) {

    let adviserRankAmountChart = canvasContainer.find('#adviserRankAmountChart');
    let adviserRankCountChart = canvasContainer.find('#adviserRankCountChart');
    this.amountChart = null;
    this.countChart = null;
    this.amount = {datasets: null};
    this.count = {datasets: null};
    this.labels = [];

    let _this = this;

    this.createChart = function () {
        let amountCtx = adviserRankAmountChart[0].getContext('2d');
        let countCtx = adviserRankCountChart[0].getContext('2d');

        amountCtx.clearRect(0, 0, adviserRankAmountChart[0].width, adviserRankAmountChart[0].height);
        countCtx.clearRect(0, 0, adviserRankCountChart[0].width, adviserRankCountChart[0].height);

        if (this.amountChart) {
            this.amountChart.destroy();
        }
        this.amountChart = chart.create(amountCtx);

        if (this.countChart) {
            this.countChart.destroy();
        }
        this.countChart = chart.create(countCtx, 'bar', '#ffffff');
    };

    function clearDatasets(datasets) {
        _this.labels=[];
        datasets['NEW'].data = [];
        datasets['ANX'].data = [];
        datasets['PRLG'].data = [];
        datasets['UGD'].data = [];
        datasets['XXX'].data = [];
    }

    this.updateChartDatasets = function () {
        let amountDatasets = [];
        let countDatasets = [];

        $("#adviserRankAgrTypeDatasetChk").find('input[type="checkbox"]:checked').each(function (i, e) {
            amountDatasets.push(_this.amount.datasets[$(e).prop('id')]);
            countDatasets.push(_this.count.datasets[$(e).prop('id')]);
        });
        _this.amountChart.data.labels = _this.labels;
        _this.amountChart.data.datasets = amountDatasets;
        _this.amountChart.update();

        _this.countChart.data.labels = _this.labels;
        _this.countChart.data.datasets = countDatasets;
        _this.countChart.update();
    };

    function getData(data) {
        let len = 0;
        clearDatasets(_this.amount.datasets);
        clearDatasets(_this.count.datasets);

        $.each(data.keys, function (i, e) {
            _this.labels.push(`${data.data[e][0].first_name} ${data.data[e][0].last_name}`);

            _this.amount.datasets['NEW'].data.push(null);
            _this.amount.datasets['ANX'].data.push(null);
            _this.amount.datasets['PRLG'].data.push(null);
            _this.amount.datasets['UGD'].data.push(null);
            _this.amount.datasets['XXX'].data.push(null);

            _this.count.datasets['NEW'].data.push(null);
            _this.count.datasets['ANX'].data.push(null);
            _this.count.datasets['PRLG'].data.push(null);
            _this.count.datasets['UGD'].data.push(null);
            _this.count.datasets['XXX'].data.push(null);

            $.each(data.data[e], function (i1, e1) {
                if (AGR_TYPE.indexOf(e1.agr_type) > -1) {
                    _this.amount.datasets[e1.agr_type].data[len] = e1.sum_val;
                    _this.count.datasets[e1.agr_type].data[len] = e1.cnt;
                }
            });
            len++;
        });
    }

    this.renderData = function (data) {
        getData(data);
        _this.updateChartDatasets();
    };

    this.collectData = function () {
        this.createChart();
    };

    function init() {
        _this.amount.datasets = initialDatasets();
        _this.count.datasets = initialDatasets();
        _this.createChart();
    }

    init();

};

export default AdviserRank;