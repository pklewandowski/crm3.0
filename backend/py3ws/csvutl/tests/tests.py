import json

from py3ws.csvutl import csvutl, validator
from py3ws.csvutl import csvvalidator3
from py3ws.csvutl.tests.config import csv_data_validators


def test_happy_path():
    csv = '"COL1";"COL2"\n"1";"Ala"\n"2";"Makota"'
    try:
        result = csvutl.process_csv(data=csv, source_header=["COL1", "COL2"], validators=csv_data_validators)
        assert len(result) == 2
        assert 'col1' in result[0]
        assert 'col2' in result[0]

    except csvutl.CsvValidationError as ex:
        assert False


def test_incorrect_type():
    csv = '"COL1";"COL2"\n"Ala";"Makota"'
    try:
        csvutl.process_csv(data=csv, source_header=["COL1", "COL2"], validators=csv_data_validators)
        assert False

    except csvutl.CsvValidationError as ex:
        e = json.loads(str(ex))
        assert e[0]['code'] == validator.VALUE_CHECK_FAILED_NOT_INT


def test_incorrect_header():
    csv = '"C1";"C2"\n"Ala";"Makota"'
    try:
        csvutl.process_csv(data=csv, source_header=["COL1", "COL2"])
        assert False
    except csvutl.CsvValidationError as ex:
        e = json.loads(str(ex))
        assert e[0]['code'] == csvvalidator3.HEADER_CHECK_FAILED


def test_not_unique():
    csv = '"COL1";"COL2"\n"1";"Makota"\n"2";"Makota"'
    try:
        csvutl.process_csv(data=csv, source_header=["COL1", "COL2"], validators=csv_data_validators)
        assert False
    except csvutl.CsvValidationError as ex:
        e = json.loads(str(ex))
        assert e[0]['code'] == validator.UNIQUE_ID_CHECK_FAILED
