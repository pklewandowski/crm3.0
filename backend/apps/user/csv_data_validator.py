

from py3ws.csvutl import validator


class CsvDataValidation:
    validators = {
        "pesel": validator.VALIDATOR_TYPE_NUMERIC
    }
