class CompanyNumbersValidator {

    static isValidNip(nip) {
        if (typeof nip !== 'string')
            return false;

        nip = nip.replace(/[\ \-]/gi, '');

        let weight = [6, 5, 7, 2, 3, 4, 5, 6, 7];
        let sum = 0;
        let controlNumber = parseInt(nip.substring(9, 10));
        let weightCount = weight.length;
        for (let i = 0; i < weightCount; i++) {
            sum += (parseInt(nip.substr(i, 1)) * weight[i]);
        }
        return sum % 11 === controlNumber;
    }

    /**
     * Sprawdza czy podany numer księgi wieczystej jest prawidłowy
     * @param {string} kw - numer księgi wieczystej do walidacji (numer musi byc w formie xxxx/xxxxxxxx/x)
     * @return {boolean} - zwraca true jeżeli podany numer jest prawidłowy, false w przeciwnym wypadku
     */
    static validateKW(kw) {
//Check length
        if (kw == null)
            return false;
        if (kw.length != 15)
            return false;

        kw = kw.toUpperCase();
        let letterValues = [
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'X',
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
            'K', 'L', 'M', 'N', 'O', 'P', 'R', 'S', 'T', 'U',
            'W', 'Y', 'Z'];

        function getLetterValue(letter) {
            for (let j = 0; j < letterValues.length; j++)
                if (letter === letterValues[j])
                    return j;
            return -1;
        }

//Check slashes
        if (kw[4] !== '/' || kw[13] !== '/')
            return false;

//Check court id
        for (let i = 0; i < 2; i++)
            if (getLetterValue(kw[i]) < 10)
                return false;

        if (getLetterValue(kw[2]) < 0 || getLetterValue(kw[2]) > 9)
            return false;

        if (getLetterValue(kw[3]) < 10)
            return false;

//Check numbers
        for (i = 5; i < 13; i++)
            if (getLetterValue(kw[i]) < 0 || getLetterValue(kw[i]) > 9)
                return false;

//Check checkdigit
        let sum = 1 * getLetterValue(kw[0]) +
            3 * getLetterValue(kw[1]) +
            7 * getLetterValue(kw[2]) +
            1 * getLetterValue(kw[3]) +
            3 * getLetterValue(kw[5]) +
            7 * getLetterValue(kw[6]) +
            1 * getLetterValue(kw[7]) +
            3 * getLetterValue(kw[8]) +
            7 * getLetterValue(kw[9]) +
            1 * getLetterValue(kw[10]) +
            3 * getLetterValue(kw[11]) +
            7 * getLetterValue(kw[12]);
        sum %= 10;

        if (kw[14] !== sum)
            return false;

        return true;
    }
}

export default CompanyNumbersValidator;