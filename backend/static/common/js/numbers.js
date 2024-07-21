function formatCurrency(val, nullValue) {
    if (isNumber(val))
        return parseFloat(val).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&\ ').replace(/\./g, ',');
    else
        return nullValue ? nullValue: '';
}

function formatIntegerThousands(val) {
    return val.replace(/(\d)(?=(\d{3})+(?!\d))/g, "$1 ");
}