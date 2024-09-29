import {ProductDashboard} from "../dashboard/js/product-dashboard";

function calculateProductAggregates(product) {
    let instalmentMcSum = 0;
    let instalmentBalloon = 0;
    if (product.data?.schedule?.length) {
        for (let i = 0; i < product.data.schedule.length - 1; i++) {
            instalmentMcSum +=
                parseFloat(product.data.schedule[i].instalment_capital) +
                parseFloat(product.data.schedule[i].instalment_commission) +
                parseFloat(product.data.schedule[i].instalment_interest);
        }

        let lastIdx = product.data.schedule.length - 1;
        instalmentBalloon =
            parseFloat(product.data.schedule[lastIdx].instalment_capital) +
            parseFloat(product.data.schedule[lastIdx].instalment_commission) +
            parseFloat(product.data.schedule[lastIdx].instalment_interest);
    }
    return {
        status: product.data?.product?.status?.name,
        startDate: product.data?.product?.start_date,
        instalmentCount: product.data?.schedule ? product.data.schedule.length : 0,
        instalmentMcSum: instalmentMcSum,
        instalmentBalloon: instalmentBalloon,
        paymentCount: product.data?.cashflow ? product.data.cashflow.filter(x => x.type.code === 'PAYMENT').length : 0
    };
}


export {calculateProductAggregates}