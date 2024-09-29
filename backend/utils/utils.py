import datetime
import importlib
import itertools
import datedelta


def get_class(full_name):
    if not full_name:
        return None
    module_name, class_name = full_name.rsplit(".", 1)
    return getattr(importlib.import_module(module_name), class_name)


def myimport(name):
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def add_month(dt, m):
    return dt + datedelta.datedelta(months=m)


def replace_special_chars(s):
    for c in ['/', '\\', ':', ' ', '&', '?', '*', '<', '>']:
        s = s.replace(c, '_')
    return s


def days_in_year(year):
    return (datetime.date(year, 12, 31) - datetime.date(year, 1, 1)).days + 1


def translate_pl_to_latin(text):
    ltr_PL = "ŻÓŁĆĘŚĄŹŃżółćęśąźń"
    ltrno_PL = "ZOLCESAZNzolcesazn"
    trans_tab = str.maketrans(ltr_PL, ltrno_PL)

    return text.translate(trans_tab)



# TODO: tylko zajawka nie działa, opracować!!!!
def xor(s, key):
    key = key * int((len(s) / len(key) + 1))
    return ''.join(chr(ord(x) ^ ord(y)) for (x, y) in itertools.izip(s, key))


def xor_crypt_string(data, key='awesomepassword', encode=False, decode=False):
    from itertools import cycle
    import base64
    if decode:
        data = base64.decodebytes(data)
    xored = ''.join(chr(ord(x) ^ ord(y)) for (x, y) in zip(data, cycle(key)))
    if encode:
        return base64.decodebytes(xored).strip()
    return xored
