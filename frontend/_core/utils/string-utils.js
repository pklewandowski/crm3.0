class StringUtils {
    static initCap(string) {
        return string.charAt(0).toUpperCase() + string.slice(1).toLowerCase();
    }

    // with single replace as whitespaces wrapped into regex expressoin
    static camelCase(str, breakChar = '_') {
        // /(?:^\w|[A-Z]|\b\w|\s+)/g;
        let dummy = new RegExp("(?:_\\w)", "g"); //    /(?:_\w)/g;
        return str.replace(dummy, function (match, index) {
            return index === 0 ? match.toLowerCase() : match.toUpperCase();
        }).replace(new RegExp(`\\${breakChar}`, "g"), '');
    }

    static toProperTitleCase(str) {
        let noCaps = ['bez', 'dla', 'do', 'i', 'ku', 'między', 'na', 'nad', 'o', 'po', 'pod', 'przed', 'przez', 'w', 'z', 'za'];
        return str.replace(/\w\S*/g, function (txt, offset) {
            if (offset != 0 && noCaps.indexOf(txt.toLowerCase()) != -1) {
                return txt.toLowerCase();
            }
            return txt.charAt(0).toUpperCase() + txt.substring(1).toLowerCase();
        });
    }
}

export default StringUtils;