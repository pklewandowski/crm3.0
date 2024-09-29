import json

from py3ws.csvutl import csvvalidator3
from py3ws.utils.validators import pesel_validator, nip_validator, krs_validator, email_validator

VALIDATOR_TYPE_INT = 1000
VALIDATOR_TYPE_NUMERIC = 1001
VALIDATOR_TYPE_ENUM = 1002
VALIDATOR_TYPE_GLOBAL_UNIQUE = 1003
VALIDATOR_TYPE_EMAIL = 1004
VALIDATOR_TYPE_NOT_NULL = 1005
VALIDATOR_TYPE_PESEL = 1006
VALIDATOR_TYPE_NIP = 1007
VALIDATOR_TYPE_KRS = 1008

VALUE_CHECK_FAILED_NOT_INT = 10
VALUE_CHECK_FAILED_NOT_NUMERIC = 11
VALUE_CHECK_FAILED_ENUM = 12
UNIQUE_ID_CHECK_FAILED = 13
VALID_TYPES_CHECK_FAILED = 14
VALUE_CHECK_FAILED_NOT_EMAIL = 15
VALUE_CHECK_FAILED_NOT_NULL = 16
VALUE_CHECK_FAILED_NOT_PESEL = 17
VALUE_CHECK_FAILED_NOT_NIP = 18
VALUE_CHECK_FAILED_NOT_KRS = 19
VALUE_CHECK_FAILED_NOT_PHONE = 20

ERR_MSG = {
    csvvalidator3.HEADER_CHECK_FAILED: '[HEADER_CHECK_FAILED] Nieprawidłowy nagłówek pliku',
    csvvalidator3.RECORD_LENGTH_CHECK_FAILED: '[RECORD_LENGTH_CHECK_FAILED] Niepoprawna długość rekordu danych',
    VALUE_CHECK_FAILED_NOT_INT: "[VALUE_CHECK_FAILED_NOT_INT] Kolumna '{}' posiada nieprawidłowy typ. Wartość powinna być liczbą całkowitą",
    VALUE_CHECK_FAILED_NOT_NULL: "[VALUE_CHECK_FAILED_NOT_NULL] Kolumna '{}' musi posiadać wartość",
    VALUE_CHECK_FAILED_NOT_NUMERIC: "[VALUE_CHECK_FAILED_NOT_NUMERIC] Kolumna '{}' posiada nieprawidłowy typ. Wartość powinna być ciągiem cyfr",
    VALUE_CHECK_FAILED_NOT_EMAIL: "[VALUE_CHECK_FAILED_NOT_EMAIL] Kolumna '{}' posiada nieprawidłowy adres email",
    VALUE_CHECK_FAILED_NOT_PESEL: "[VALUE_CHECK_FAILED_NOT_PESEL] Kolumna '{}' posiada nieprawidłowy numer PESEL",
    VALUE_CHECK_FAILED_NOT_NIP: "[VALUE_CHECK_FAILED_NOT_NIP] Kolumna '{}' posiada nieprawidłowy numer NIP",
    VALUE_CHECK_FAILED_NOT_KRS: "[VALUE_CHECK_FAILED_NOT_KRS] Kolumna '{}' posiada nieprawidłowy numer KRS",
    VALUE_CHECK_FAILED_ENUM: "[VALUE_CHECK_FAILED_ENUM] Kolumna '{}' posiada niedozwoloną wartość.",
    UNIQUE_ID_CHECK_FAILED: "Kolumna {} musi posiadać wartości unikalne",
    VALID_TYPES_CHECK_FAILED: "Kolumna {} musi posiadać wartości typu {}"
}


class CsvValidatorException(Exception):
    pass


def _error_message(code, message, record, row, field, missing=None):
    if missing is None:
        missing = []
    return {
        'code': code,
        'message': message,
        'record': record,
        'field': field,
        'row': row,
        'missing': missing
    }


def _map_csv_validator_error(err):
    return _error_message(
        code=err['code'],
        message=err['message'],
        record=err['record'],
        field=err['field'] if 'field' in err else '',
        missing=list(err['missing']) if 'missing' in err else [],
        row=err['row']
    )


def csv_validator_wrapper(fn):
    def wrapper(value):
        if value is None or value == '':
            return
        try:
            fn(value)
        except Exception:
            raise ValueError

    return wrapper


def _format_validation_errors(errors):
    error_list = {}

    for err in errors:
        if err['row'] not in error_list:
            error_list[err['row']] = [_map_csv_validator_error(err)]
        else:
            error_list[err['row']].append(_map_csv_validator_error(err))
    return error_list


def _validate_not_null(value):
    if value is None or value == '':
        raise ValueError


@csv_validator_wrapper
def _validate_numeric(value):
    if not value.isnumeric():
        raise


@csv_validator_wrapper
def _validate_email(value):
    return email_validator(value)


@csv_validator_wrapper
def _validate_pesel(value):
    return pesel_validator(value)


@csv_validator_wrapper
def _validate_nip(value):
    return nip_validator(value)


@csv_validator_wrapper
def _validate_krs(value):
    return krs_validator(value)


def _add_validators(validator, validators):
    if validators:
        for vd in validators:
            if vd['type'] == VALIDATOR_TYPE_NOT_NULL:
                validator.add_value_check(field_name=vd["column"], value_check=_validate_not_null,
                                          code=VALUE_CHECK_FAILED_NOT_NULL,
                                          message=ERR_MSG[VALUE_CHECK_FAILED_NOT_NULL].format(vd["column"]))
            elif vd['type'] == VALIDATOR_TYPE_INT:
                validator.add_value_check(field_name=vd["column"], value_check=int,
                                          code=VALUE_CHECK_FAILED_NOT_INT,
                                          message=ERR_MSG[VALUE_CHECK_FAILED_NOT_INT].format(vd["column"]))
            elif vd['type'] == VALIDATOR_TYPE_NUMERIC:
                validator.add_value_check(field_name=vd["column"], value_check=_validate_numeric,
                                          code=VALUE_CHECK_FAILED_NOT_NUMERIC,
                                          message=ERR_MSG[VALUE_CHECK_FAILED_NOT_NUMERIC].format(vd["column"]))
            elif vd['type'] == VALIDATOR_TYPE_EMAIL:
                validator.add_value_check(field_name=vd["column"], value_check=_validate_email,
                                          code=VALUE_CHECK_FAILED_NOT_EMAIL,
                                          message=ERR_MSG[VALUE_CHECK_FAILED_NOT_EMAIL].format(vd["column"]))
            elif vd['type'] == VALIDATOR_TYPE_ENUM:
                validator.add_value_check(field_name=vd["column"], value_check=vd["class"],
                                          code=VALUE_CHECK_FAILED_ENUM,
                                          message=ERR_MSG[VALUE_CHECK_FAILED_ENUM].format(vd["column"]))
            elif vd['type'] == VALIDATOR_TYPE_GLOBAL_UNIQUE:
                validator.add_unique_check(key=vd["column"],
                                           message=ERR_MSG[UNIQUE_ID_CHECK_FAILED].format(vd["column"]))
            elif vd['type'] == VALIDATOR_TYPE_PESEL:
                validator.add_value_check(field_name=vd["column"], value_check=_validate_pesel,
                                          code=VALUE_CHECK_FAILED_NOT_PESEL,
                                          message=ERR_MSG[VALUE_CHECK_FAILED_NOT_PESEL].format(vd["column"]))
            elif vd['type'] == VALIDATOR_TYPE_NIP:
                validator.add_value_check(field_name=vd["column"], value_check=_validate_nip,
                                          code=VALUE_CHECK_FAILED_NOT_NIP,
                                          message=ERR_MSG[VALUE_CHECK_FAILED_NOT_NIP].format(vd["column"]))
            elif vd['type'] == VALIDATOR_TYPE_KRS:
                validator.add_value_check(field_name=vd["column"], value_check=_validate_krs,
                                          code=VALUE_CHECK_FAILED_NOT_KRS,
                                          message=ERR_MSG[VALUE_CHECK_FAILED_NOT_KRS].format(vd["column"]))


def validate_csv(data, header, validators=None):
    validator = csvvalidator3.CSVValidator3(header)

    validator.add_header_check(message=ERR_MSG[csvvalidator3.HEADER_CHECK_FAILED])
    errors = list(validator.validate(data))
    if errors:
        raise CsvValidatorException(json.dumps(_format_validation_errors(errors)))

    validator.add_record_length_check(message=ERR_MSG[csvvalidator3.RECORD_LENGTH_CHECK_FAILED])
    errors = list(validator.validate(data))
    if errors:
        raise CsvValidatorException(json.dumps(_format_validation_errors(errors)))

    _add_validators(validator, validators)
    return _format_validation_errors(validator.validate(data))
