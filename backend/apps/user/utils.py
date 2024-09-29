import random
import re
import string

from django.conf import settings

from apps.user.models import User
from py3ws.utils import utils as py3ws_utils


def generate_password(symbols=False):
    length = settings.INITIAL_PASSWORD_LENGTH if getattr(settings, 'INITIAL_PASSWORD_LENGTH', None) else 30
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    num = string.digits

    combined = lower + upper + num

    if symbols:
        _symbols = "".join([i for i in string.punctuation if i not in ['~', '"', "'", '^', ',', '.']])
        combined += _symbols

    return "".join(random.sample(combined, length))


def set_username(first_name, last_name, company_name):
    i = ''
    if not last_name and not company_name:
        raise AttributeError('Pole nazwisko lub nazwa firmy jest konieczne do wygenerowania loginu')
    _username = (first_name[0] if first_name else '').lower() + (last_name.lower() if last_name else company_name.lower())
    _username = py3ws_utils.translate_pl_to_latin(_username)
    _username = re.sub(r'\s+', '', _username)
    _username = re.sub(r'[^a-zA-Z]', '', _username)
    _username = _username.strip()

    while True:
        username = _username + str(i)

        try:
            User.objects.get(username=username)
            if i == '':
                i = 1
            else:
                i += 1
        except User.DoesNotExist:
            return username


def get_user(id):
    if not id:
        return None
    try:
        return User.objects.get(pk=id)
    except User.DoesNotExist:
        return None
