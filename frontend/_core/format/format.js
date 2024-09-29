
class Format {
//currency formatting
    static formatNumber(cell, formatterParams, accountingStyle = false) {
        let floatVal = parseFloat(cell),
            number,
            integer,
            decimal,
            rgx;

        let decimalSym = formatterParams?.decimal || ",";
        let thousandSym = formatterParams?.thousand || " ";
        let symbol = formatterParams?.symbol || "";
        let after = !!formatterParams?.symbolAfter;
        let precision = typeof formatterParams?.precision !== "undefined" ? formatterParams.precision : 2;

        if (isNaN(floatVal)) {
            return cell;
        }

        if (floatVal === 0 && accountingStyle) {
            return '-';
        }

        number = precision !== false ? floatVal.toFixed(precision) : floatVal;
        number = String(number).split(".");

        integer = number[0];
        decimal = number.length > 1 ? decimalSym + number[1] : "";

        rgx = /(\d+)(\d{3})/;

        while (rgx.test(integer)) {
            integer = integer.replace(rgx, "$1" + thousandSym + "$2");
        }

        return after ? integer + decimal + symbol : symbol + integer + decimal;
    }

    static formatCurrency(val, nullValue) {
        if (isNumber(val))
            return parseFloat(val).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&\ ').replace(/\./g, ',');
        else
            return nullValue ? nullValue : '';
    }

    static formatIntegerThousands(val) {
        return val.replace(/(\d)(?=(\d{3})+(?!\d))/g, "$1 ");
    }
}

export {Format};