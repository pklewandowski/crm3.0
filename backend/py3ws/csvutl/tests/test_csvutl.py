import json
import os

from py3ws.csvutl import csvutl, validator
from py3ws.csvutl import csvvalidator3
from py3ws.csvutl.tests.config import csv_data_validators
from py3ws.csvutl.validator import CsvValidatorException


def test_happy_path():
    csv = '"COL1";"COL2"\n"1";"Ala"\n"2";"Makota"'
    try:
        result = csvutl.process_csv(data=csv, source_header=["COL1", "COL2"], validators=csv_data_validators)
        assert len(result) == 2
        assert 'col1' in result[0]
        assert 'col2' in result[0]

    except CsvValidatorException as ex:
        assert False


def test_real_file():
    with open(os.path.join(os.path.dirname(__file__), 'test_data/klienci_test.csv'), encoding='utf8') as f:
        result = csvutl.process_csv(data=f,
                                    source_header=["Imię", "Nazwisko", "Nazwa Firmy", "tagi", "telefon", "mail", "opiekun", "PESEL", "NIP", "REGON", "KRS", "Miasto", "ulica", "nr", "nr lokalu",
                                                   "kod pocztowy"])
        assert len(result) == 10


def test_incorrect_type():
    csv = '"COL1";"COL2"\n"Ala";"Makota"'
    try:
        csvutl.process_csv(data=csv, source_header=["COL1", "COL2"], validators=csv_data_validators)
        assert False

    except CsvValidatorException as ex:
        e = json.loads(str(ex))
        assert e[0]['code'] == validator.VALUE_CHECK_FAILED_NOT_INT


def test_incorrect_header():
    csv = '"C1";"C2"\n"Ala";"Makota"'
    try:
        csvutl.process_csv(data=csv, source_header=["COL1", "COL2"])
        assert False
    except CsvValidatorException as ex:
        e = json.loads(str(ex))
        assert e[0]['code'] == csvvalidator3.HEADER_CHECK_FAILED


def test_not_unique():
    csv = '"COL1";"COL2"\n"1";"Makota"\n"2";"Makota"'
    try:
        csvutl.process_csv(data=csv, source_header=["COL1", "COL2"], validators=csv_data_validators)
        assert False
    except CsvValidatorException as ex:
        e = json.loads(str(ex))
        assert e[0]['code'] == validator.UNIQUE_ID_CHECK_FAILED


def test_not_numeric():
    csv = '"COL1";"COL2";"COL3"\n"1";"Makota";"1234554798769567579567956587568056"\n"2";"Makota1";"notnumeric"'
    csv_data_validator = csv_data_validators.copy()
    csv_data_validator.append({"column": "COL3", "type": validator.VALIDATOR_TYPE_NUMERIC})
    try:
        csvutl.process_csv(data=csv, source_header=["COL1", "COL2", "COL3"], validators=csv_data_validator)
        assert False
    except CsvValidatorException as ex:
        e = json.loads(str(ex))
        assert e[0]['code'] == validator.VALUE_CHECK_FAILED_NOT_NUMERIC


def test_bad_pesel():
    csv = '"COL1";"COL2";"COL3"\n"1";"Makota";"32323232321"\n"2";"Makota1";"bad pesel"'
    csv_data_validator = csv_data_validators.copy()
    csv_data_validator.append({"column": "COL3", "type": validator.VALIDATOR_TYPE_PESEL})
    try:
        csvutl.process_csv(data=csv, source_header=["COL1", "COL2", "COL3"], validators=csv_data_validator)
        assert False
    except CsvValidatorException as ex:
        e = json.loads(str(ex))
        assert e[0]['code'] == validator.VALUE_CHECK_FAILED_NOT_PESEL


def test_good_pesel():
    csv = '"COL1";"COL2";"COL3"\n"1";"Makota";"50110891393"\n"2";"Makota1";"02281351417"'
    csv_data_validator = csv_data_validators.copy()
    csv_data_validator.append({"column": "COL3", "type": validator.VALIDATOR_TYPE_PESEL})
    try:
        csvutl.process_csv(data=csv, source_header=["COL1", "COL2", "COL3"], validators=csv_data_validator)
        assert True
    except CsvValidatorException as ex:
        assert False


def test_bad_email():
    csv = '"COL1";"COL2";"COL3"\n"1";"Makota";"good.email@example.com"\n"2";"Makota1";"bad email"'
    csv_data_validator = csv_data_validators.copy()
    csv_data_validator.append({"column": "COL3", "type": validator.VALIDATOR_TYPE_EMAIL})
    try:
        csvutl.process_csv(data=csv, source_header=["COL1", "COL2", "COL3"], validators=csv_data_validator)
        assert False
    except CsvValidatorException as ex:
        e = json.loads(str(ex))
        assert e[0]['code'] == validator.VALUE_CHECK_FAILED_NOT_EMAIL


def test_good_email():
    csv = '"COL1";"COL2";"COL3"\n"1";"Makota";"good.email@example.com"\n"2";"Makota1";"good1.email@example.com"'
    csv_data_validator = csv_data_validators.copy()
    csv_data_validator.append({"column": "COL3", "type": validator.VALIDATOR_TYPE_EMAIL})
    try:
        csvutl.process_csv(data=csv, source_header=["COL1", "COL2", "COL3"], validators=csv_data_validator)
    except CsvValidatorException:
        assert False


def test_process_csv_happy_path():
    header = 'Imię;Nazwisko;Nazwa Firmy;tagi;telefon;mail;opiekun;PESEL;NIP;REGON;KRS;Miasto;ulica;nr;nr lokalu;kod pocztowy'
    csv_schema = [
        {"column": "user.first_name", "csv_header": "Imię", "validators": []},
        {"column": "user.last_name", "csv_header": "Nazwisko", "validators": []},
        {"column": "user.company_name", "csv_header": "Nazwa Firmy", "validators": []},
        {"column": "user.tags", "csv_header": "tagi", "validators": []},
        {"column": "user.phone_one", "csv_header": "telefon", "validators": [validator.VALIDATOR_TYPE_NUMERIC]},
        {"column": "user.email", "csv_header": "mail", "validators": [validator.VALIDATOR_TYPE_EMAIL, validator.VALIDATOR_TYPE_NOT_NULL, validator.VALIDATOR_TYPE_GLOBAL_UNIQUE]},
        {"column": "client.adviser", "csv_header": "opiekun", "validators": []},
        {"column": "user.pesel", "csv_header": "PESEL", "validators": [validator.VALIDATOR_TYPE_PESEL, validator.VALIDATOR_TYPE_NOT_NULL, validator.VALIDATOR_TYPE_GLOBAL_UNIQUE]},
        {"column": "user.nip", "csv_header": "NIP", "validators": [validator.VALIDATOR_TYPE_NIP]},
        {"column": "user.regon", "csv_header": "REGON", "validators": []},
        {"column": "user.krs", "csv_header": "KRS", "validators": [validator.VALIDATOR_TYPE_KRS]},
        {"column": "address.city", "csv_header": "Miasto", "validators": []},
        {"column": "address.street", "csv_header": "ulica", "validators": []},
        {"column": "address.street_no", "csv_header": "nr", "validators": []},
        {"column": "address.apartment_no", "csv_header": "nr lokalu", "validators": []},
        {"column": "address.email", "csv_header": "kod pocztowy", "validators": []}
    ]
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data/klienci_test.csv'), encoding='utf-8') as file:
        try:
            result = csvutl.process_csv(data=file, source_header=header.split(';'), validators=csvutl.build_validators(csv_schema))
            assert len(result) == 10
        except CsvValidatorException:
            assert False


def test_write_csv():
    path = '/tmp/csv_temp_file.csv'
    header = ['FIRST_NAM"E', 'LAST_NAME']
    data = [
        ['Ala', 'Mak"";ota'],
        ['Kot', 'Maa""le']
    ]
    csvutl.write_csv(path=path, data=data, header=header)
