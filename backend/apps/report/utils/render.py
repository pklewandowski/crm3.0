import datetime
import re
from datetime import timedelta

import jinja2
from jinja2 import BaseLoader

from apps.address.models import Address


def percent_formatter(v):
    return float(v) * 100 if v else v


def mobile_number_formatter(v):
    r = r'(\+\d{2})?(\d{3})(\d{3})(\d{3})'
    return re.sub(r, r'\1 \2 \3 \4', v).strip()


def add_days(date, days):
    return datetime.datetime.strftime(
        datetime.datetime.strptime(date, '%Y-%m-%d').date() + timedelta(days=days),
        '%Y-%m-%d'
    )


def two_line_address(address):
    if not address:
        return ['', '']
    return address.get_two_line_address()


def default(value, default_text=''):
    if not value:
        return default_text
    return value


def set_jinja2_env():
    env = jinja2.Environment(loader=BaseLoader)
    env.filters['currency'] = lambda v: "{:,.2f}".format(float(v)).replace(',', ' ').replace('.', ',') if v else v
    env.filters['percent'] = percent_formatter
    env.filters['mobile_number_formatter'] = mobile_number_formatter
    env.filters['trim'] = lambda v: v.strip()
    env.filters['add_days'] = add_days
    env.filters['two_line_address'] = two_line_address
    env.filters['default'] = default

    return env


def render_html_template(html, params):
    env = set_jinja2_env()
    template = env.from_string(html)
    txt = template.render(params)

    return txt
