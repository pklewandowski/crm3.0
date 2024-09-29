import pytest

from py3ws.csvutl import validator

csv_data_validators = [
    {
        "type": validator.VALIDATOR_TYPE_INT,
        "column": "COL1",
    },
    {
        "type": validator.VALIDATOR_TYPE_GLOBAL_UNIQUE,
        "column": "COL2"
    },
]