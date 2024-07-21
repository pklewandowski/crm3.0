import {CurrentContacts} from "../../widget/currentContacts/js/current-contacts";
import {QuickMenu} from "../../widget/quickMenu/js/quick-menu";
import {Calendar} from "../../schedule/calendar/js/calendar";
import {NumberWidget} from "../../widget/number/js/number-widget";
import {Format} from "../../_core/format/format";
import {ChartControl} from "../../_core/controls/chart-control/js/chart-control";
import {IncomingEvents} from "../../widget/incomingEvents/js/incoming-events";

$(document).ready(() => {
    //number widgets

    ajaxCall({
        method: 'get',
        url: '/api/number-widget/'
    }).then(
        (resp) => {
            new NumberWidget(document.querySelector('.dashboard-clients'), resp.clients.name, resp.clients.value);
            new NumberWidget(
                document.querySelector('.dashboard-balance-sum'),
                resp.balanceSum.name,
                Format.formatNumber(resp.balanceSum.value)
            );
            new NumberWidget(document.querySelector('.dashboard-all-loan-sum'), resp.allLoanSum.name, Format.formatNumber(resp.allLoanSum.value));
            new NumberWidget(
                document.querySelector('.dashboard-instalment-income'),
                resp.instalmentIncome.name,
                Format.formatNumber(resp.instalmentIncome.value)
            );
            new NumberWidget(
                document.querySelector('.dashboard-average-loan-value'),
                resp.avgLoanVal.name,
                Format.formatNumber(resp.avgLoanVal.value)
            );
            new NumberWidget(
                document.querySelector('.dashboard-median-loan-value'),
                resp.median.name,
                Format.formatNumber(resp.median.value)
            );
        }
    );

    let options = {
        legend: {
            display: true,
            position: 'right'
        }
    };

    // todo: DRUT!!!!
    if (_g.companyCode !== 'OPENCASH') {
        ajaxCall({
            method: 'get',
            url: '/api/chart-widget/'
        }).then(
            (resp) => {
                new ChartControl(
                    document.querySelector('.dashboard-document-status-chart'),
                    resp.documentStatusChart, 'doughnut',
                    options).render();

                new ChartControl(
                    document.querySelector('.dashboard-document-by-adviser-chart'),
                    resp.documentByAdviser, 'bar',
                    Object.assign({}, options, {bgColors: 'rgb(41,156,236)'})).render();
            });
        // new ChartControl(document.querySelector('.dashboard-product-status-chart'), sampleChartDataset, 'doughnut', options).render();
    }

    let currentContacts = new CurrentContacts(document.querySelector('.current-contacts-container'), _g.home.urls, 'Bieżące kontakty');
    currentContacts.render();

    let incomingEvents = new IncomingEvents(document.querySelector('.incoming-events-container'), _g.home.urls, 'Nadchodzące wydarzenia');
    incomingEvents.render();


    let calendar = new Calendar(
        document.getElementById('calendarContainer'),
        false, null, null,
        {
            invited_users: [
                {id: _g.credentials.user.id, first_name: _g.credentials.user.first_name, last_name: _g.credentials.user.last_name}
            ],
            allowAllDayEvents: false,
            calendar: {
                slotDuration: '00:30:00',
                shortenedViewNames: true
            }
        });

    calendar.setCalendar();
});

