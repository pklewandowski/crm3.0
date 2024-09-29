import datetime
import importlib

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


# TODO: tylko zajawka, opracować!!!!
def xor(s, key):
    key = key * int((len(s) / len(key) + 1))
    return ''.join(chr(ord(x) ^ ord(y)) for (x, y) in zip(s, key))


def xor_crypt_string(data, key='awesomepassword', encode=False, decode=False):
    from itertools import cycle
    xored = ''.join(chr(ord(x) ^ ord(y)) for (x, y) in zip(data, cycle(key)))
    return xored


def merge_two_dicts(x, y):
    z = x.copy()  # start with x's keys and values
    z.update(y)  # modifies z with y's keys and values & returns None
    return z


def findkeys(node, kv):
    if isinstance(node, list):
        for i in node:
            for x in findkeys(i, kv):
                yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in findkeys(j, kv):
                yield x


def call_def_form_str(fn, val):
    module_name = ".".join(fn.split(".")[:-1])
    function_name = fn.split(".")[-1]
    m = __import__(module_name, fromlist=[''])
    return getattr(m, function_name)(val)


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
