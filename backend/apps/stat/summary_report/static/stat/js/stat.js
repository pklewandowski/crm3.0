import StatData from "./stat-data.js";


$(document).ready(function () {

    let statData = new StatData();
    statData.collectData('__all__');

    $(".btn-refresh").click(function () {
        statData.collectData('__all__');
    });

    $(".toggle-all").change(function () {
        let _this = $(this);

        $(this).closest(".filter-panel").find('.toggle-chk input[type="checkbox"]').each(function () {
            $(this).prop("checked", _this.is(":checked"));
        });
    });

    $("#income-tab").find("input.toggle-all, .toggle-chk input, #id_income-business_type").change(function () {
        statData.collectData('income');
    });
    $("#income-tab").find("input.date-field").datetimepicker().on('dp.change', function () {
        statData.collectData('income');
    });

    $("#adviserRank-tab").find("input.toggle-all, .toggle-chk input").change(function () {
        statData.collectData('adviserRank');
    });

    $("#adviserRank-tab").find("input.date-field").datetimepicker().on('dp.change', function () {
        statData.collectData('adviserRank');
    });

    $("#dynamics-tab").find("input.toggle-all, .toggle-chk input").change(function () {
        statData.collectData('dynamics');
    });

    $("#dynamics-tab").find("input.date-field").datetimepicker().on('dp.change', function () {
        statData.collectData('dynamics');
    });

    $("#adviserRankAgrTypeDatasetChk").find('input[type="checkbox"]').change(function () {
        statData.adviserRank.updateChartDatasets(); //collectData('adviserRank');
    });

    $(".toggle-chk input").change(function () {
        if ($(this).is(":checked")) {
            $(this).closest(".filter-panel").find(".toggle-all").prop("checked", true);
        }
    });

    $(".stat-filter-editable-action i.fa-times-circle").click(function () {
        let _this = $(this);
        Alert.questionWarning(
            "Czy na pewno usunąć grupę?",
            '',
            () => {
                $.ajax({
                    url: _this.data('url'),
                    method: 'post',
                    data: {id: _this.data('id'), 'csrfmiddlewaretoken': _g.csrfmiddlewaretoken},
                    success: function (resp) {
                        _this.closest(".stat-filter-group-item").remove();
                    },
                    error: function (resp) {
                        Alert.error('Wystąpił wyjątek:', resp.errmsg);
                    }
                });
            });
    });


    let canvas = document.getElementById('adviserRankAmountChart');
    canvas.onclick = function (evt) {
        let activePoint = statData.adviserRank.amountChart.getElementAtEvent(evt)[0];
        if (!activePoint) {
            return
        }
        let data = activePoint._chart.data;
        let datasetIndex = activePoint._datasetIndex;
        let label = data.datasets[datasetIndex].label;

        let value = data.datasets[datasetIndex].data[activePoint._index];
        console.log(data.labels[activePoint._index]);
    };
});


