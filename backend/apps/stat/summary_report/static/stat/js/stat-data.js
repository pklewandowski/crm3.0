import Income from "./income.js"
import Dynamics from "./dynamics/dynamics.js"
import AdviserRank from "./adviser_rank/adviser-rank.js"

const StatData = function (options) {
    let defaults = {
        incomeContainer: $("#incomeData"),
        dynamicsContainer: $("#dynamicsContainer"),
        adviserRankContainer: $("#adviserRankContainer"),
    };

    this.incomeContainer = $(options && options.incomeContainer ? options.incomeContainer : defaults.incomeContainer);
    this.dynamicsContainer = $(options && options.dynamicsContainer ? options.dynamicsContainer : defaults.dynamicsContainer);
    this.adviserRankContainer = $(options && options.adviserRankContainer ? options.adviserRankContainer : defaults.adviserRankContainer);

    this.income = new Income(this.incomeContainer);
    this.adviserRank = new AdviserRank(this.adviserRankContainer);
    this.dynamics = new Dynamics(this.dynamicsContainer);

    let _this = this;

    function render(data, dataType) {
        if (['income', '__all__'].indexOf(dataType) > -1) {
            _this.income.renderData(data.income);
        }
        if (['adviserRank', '__all__'].indexOf(dataType) > -1) {
            _this.adviserRank.renderData(data.adviserRank);
        }
        if (['dynamics', '__all__'].indexOf(dataType) > -1) {
            _this.dynamics.renderData(data.dynamics);
        }
    }

    this.collectData = function (dataType) {
        let data = $('form').serializeArray();
        data.push({name: 'csrfmiddlewaretoken', value: _g.csrfmiddlewaretoken, dataType: dataType});
        data.push({name: 'dataType', value: dataType});

        $.ajax({
            url: _g.stat.urls.getDataUrl,
            method: 'post',
            data: data,
            success: function (resp) {
                render(resp, dataType);
            },
            error: function (resp) {
                Alert.error("Błąd!", resp.responseJSON.errmsg);
            }
        });
    };
};

export default StatData;