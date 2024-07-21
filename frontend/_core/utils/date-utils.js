import {SystemException} from "../exception";

class DateUtils {

    static dateDiff(d1, d2, unit = 'days', absolute = false) {
        let divFactor = null;

        if (unit === 'days') {
            divFactor = 1000 * 60 * 60 * 24;

        } else {
            throw new SystemException(`[dateUtils:dateDiff]: '${unit}' not implemented yet`);
        }

        let result = Math.round((d2 - d1) / divFactor);

        if (absolute) {
            result = Math.abs(result);
        }
        return result;
    }

    static getHourMinuteSecond(dt) {
        return `${('0' + dt.getHours()).slice(-2)}:${('0' + dt.getMinutes()).slice(-2)}:${('0' + dt.getSeconds()).slice(-2)}`
    }

    static formatDate(date, time = false, iso = false) {
        let dt = new Date(date);

        let dtStr = `${dt.getFullYear()}-${('0' + (dt.getMonth() + 1)).slice(-2)}-${('0' + dt.getDate()).slice(-2)}`;
        if (time) {
            dtStr += `${iso ? 'T' : ' '}${this.getHourMinuteSecond(dt)}`;
        }
        return dtStr;
    }

    static formatDateTime(dt) {
        return `${DateUtils.formatDate(dt)} ${DateUtils.getHourMinuteSecond(dt)}`;
    }
}

export {DateUtils}