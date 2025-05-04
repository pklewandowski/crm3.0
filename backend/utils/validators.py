from operator import mul

from django.core.exceptions import ValidationError
import pprint


def _validate_pesel(pesel):
    if len(pesel) != 11 or not pesel.isdigit():
        return False
    return int(pesel[10]) == (100000 - sum(x * int(y) for x, y in zip([1, 3, 7, 9, 1, 3, 7, 9, 1, 3], pesel))) % 10


def _validate_nip(nip_str):
    nip_str = nip_str.replace('-', '')
    if len(nip_str) != 10 or not nip_str.isdigit() or nip_str[0] == '0':
        return False
    digits = [int(d) for d in list(nip_str)]
    weights = (6, 5, 7, 2, 3, 4, 5, 6, 7)
    check_sum = sum(map(mul, digits[0:9], weights)) % 11
    return check_sum == digits[9]


def _validate_krs(krs):
    if len(krs) != 10 or not krs.isdigit():
        return False
    return True


def pesel_validator(pesel):
    valid = _validate_pesel(pesel)
    if not valid:
        raise ValidationError('Niepoprawny numer PESEL!')


def nip_validator(nip):
    valid = _validate_nip(nip)
    if not valid:
        raise ValidationError('Niepoprawny numer NIP!')


def krs_validator(krs):
    valid = _validate_krs(krs)
    if not valid:
        raise ValidationError('Niepoprawny numer KRS!')
