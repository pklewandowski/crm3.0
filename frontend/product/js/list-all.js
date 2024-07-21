import {ChartControl} from "../../_core/controls/chart-control/js/chart-control";
import {NumberWidget} from "../../widget/number/js/number-widget";

let options = {
        legend: {
            display: true,
            position: 'bottom'
        }
    };

ajaxCall({
    method: 'get',
    url: '/product/api/product-stats/'
}).then(
    (resp) => {
        new ChartControl(document.getElementById('product-stats'), resp.productStatsChart, 'doughnut', options).render();
        new NumberWidget(document.getElementById('product-stats-sum'), resp.clients.name, resp.clients.value);

    });
