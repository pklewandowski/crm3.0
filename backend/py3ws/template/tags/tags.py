"""
You have to add this library to OPTIONS->builtins of TEMPLATES in settings.py in case to use it in all tempaltes, the way like this:
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            (os.path.join(BASE_DIR, 'templates'))
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                ...
            ],
            'builtins': ['py3ws.template.tags.tags'],
        },
    },
]
"""
import datetime
import json
import logging
import types
from copy import copy
from uuid import uuid4

from babel.numbers import format_decimal
from django import template
from django.conf import settings
from django.templatetags.static import static
from django.utils.translation import to_locale, get_language

from apps.address.models import Address
from apps.attachment import utils as atm_utils
from py3ws.utils import utils


def silence_without_field(fn):
    def wrapped(field, attr):
        if not field:
            return ""
        return fn(field, attr)

    return wrapped


def dict_label_from_id(id, code):
    dict_class = settings.DICTIONARY_CLASS

    if not dict_class:
        return ''

    cl = utils.myimport(dict_class)

    try:
        dict = cl.objects.get(dictionary__code=code, pk=id)
        return dict.label
    except:
        return ''


register = template.Library()


@register.filter(name='list_str_to_int')
def list_str_to_int(list_array):
    return list(map(int, list_array))


@register.filter(name='datetime_to_str')
def datetime_to_str(datetime_val, format=None):
    if not datetime_val:
        return ''
    if not format:
        return datetime_val.strftime('%Y-%m-%dT%H:%M:%S')
    else:
        return datetime_val.strftime(format)


@register.filter(name='list_index')
def list_index(list, i):
    if list[int(i)]:
        return 'true'
    else:
        return 'false'


@register.filter(name='get_attr')
def get_attr(e, attr_name):
    return e.field.widget.attrs[attr_name]


@register.filter(name='replace_prefix')
def replace_prefix(value, replacement):
    return value.replace('__prefix__', str(replacement))


@register.filter(name='divide_int')
def divide_int(value, div):
    return int(value / div)


@register.filter(name='max_value')
def max_value(value, max_val):
    if value is None or max_value is None:
        return None
    return max(value, max_val)


@register.filter(name='percent')
def max_value(value):
    if not value:
        return ''
    return value * 100


@register.filter(name='get_key')
def get_key(e, key):
    if type(e) in (tuple, list, dict):
        return e[key]
    else:
        return None


@register.filter(name='l_txt')
def lvm_txt(e):
    if e:
        j = json.loads(e)
        return j
    else:
        return None


@register.filter(name='lv_txt')
def lv_txt(e, code):
    # try:
    if e:

        if e['dtc']:
            return dict_label_from_id(int(e['dtc']), code)
        elif e['custom']:
            return e['custom']

        return ''

    else:
        return ''
        # except:
        #   return ''


@register.filter(name='dict_equal')
def dict_equal(dict_id, val):
    if type(val) in (tuple, list, dict):
        for i in val:
            if str(dict_id) == str(i):
                return True
        return False
    else:
        return str(dict_id) == str(val)


@register.filter(name='dot_if_null')
def dot_if_null(e, cnt):
    if not e:
        d = ''
        for i in range(0, cnt):
            d += '.'
        return d
    else:
        return e


@register.filter(name='classname')
def classname(e):
    if e:
        return e.__class__.__name__
    else:
        return ''


@register.filter(name='compact_address')
def compact_address(e):
    if isinstance(e, Address):
        return e.get_compact_address()
    return ''

    # try:
    #     if not e.street:
    #         return ''
    #
    #     return (e.street_prefix.lower() + '. ' if e.street_prefix else '') \
    #            + e.street + ' ' + (str(e.street_no) if e.street_no else '') + (' lok. ' + str(e.apartment_no) if e.apartment_no else '') + ', ' \
    #            + (e.post_code if e.post_code else '') + ' ' + (e.city if e.city else '')
    # except AttributeError:
    #     return ''


@register.filter(name='times')
def times(number):
    return range(number)


@register.filter(name='float_or_dash')
def float_or_dash(v):
    if v is None or v == 0 or type(v) is str:
        return '-'
    return nformat('%0.2f' % v)


@register.filter(name='get_form_field')
def get_form_field(e, field):
    try:
        return e[field]
    except Exception:
        return None


@register.filter(name='readonly')
def readonly(field):
    field.as_widget(attrs={"readonly": "readonly"})
    return field


@register.filter(name='prev_val')
def prev_val(field, value):
    field.as_widget(attrs={"data-prev_val": value})
    return field


@register.filter(name='split')
def split(value, arg):
    return value.split(arg)


@register.filter(name='to_json')
def to_json(value):
    if not value:
        return []
    try:
        return json.loads(value)
    except Exception:
        return []


@register.filter(name='mime_type_icon')
def mime_type_icon(value, size):
    try:
        if not value:
            return ''
        return static('attachment/img/file_types' + atm_utils.get_mime_type(value.split(".")[-1])[f'icon_{size}'])
    except KeyError as ex:
        logging.log(logging.ERROR, ex)
        return ''


def _process_field_attributes(field, attr, process):
    # split attribute name and value from 'attr:value' string
    params = attr.split(':', 1)
    attribute = params[0]
    value = params[1] if len(params) == 2 else ''

    field = copy(field)

    # decorate field.as_widget method with updated attributes
    old_as_widget = field.as_widget

    def as_widget(self, widget=None, attrs=None, only_initial=False):
        attrs = attrs or {}
        process(widget or self.field.widget, attrs, attribute, value)
        html = old_as_widget(widget, attrs, only_initial)
        self.as_widget = old_as_widget
        return html

    field.as_widget = types.MethodType(as_widget, field)
    return field


@register.filter("attr")
@silence_without_field
def set_attr(field, attr):
    def process(widget, attrs, attribute, value):
        attrs[attribute] = value

    return _process_field_attributes(field, attr, process)


@register.filter(name='addcss')
def addcss(field, css):
    return field.as_widget(attrs={"class": css})


@register.filter(name='addstr')
def addstr(arg1, arg2):
    """concatenate arg1 & arg2"""
    return str(arg1) + str(arg2)


@register.simple_tag(name='config_var')
def config_var(var):
    return getattr(settings, var, None)


@register.filter('fieldtype')
def fieldtype(field):
    return field.field.widget.__class__.__name__


@register.simple_tag(name='dict_label')
def dict_label(value, code):
    dict_class = settings.DICTIONARY_CLASS

    if not dict_class:
        return ''

    cl = utils.myimport(dict_class)

    try:
        dict = cl.objects.get(dictionary__code=code, value=value)
        return dict.label
    except:
        return ''


@register.filter('order_by')
def order_by(queryset, args):
    args = [x.strip() for x in args.split(',')]
    return queryset.order_by(*args)


@register.filter('addstr')
def addstr(arg1, arg2):
    """concatenate arg1 & arg2"""
    return str(arg1) + str(arg2)


@register.simple_tag(name='get_default_form_input_class')
def get_default_form_input_class():
    return settings.FORM_FIELD_BASE_CSS_CLASS or 'form-control input-md'


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_management_form(formset):
    return formset.management_form


@register.filter
def json_dumps(val):
    return json.dumps(val)


@register.simple_tag(name='uuid')
def uuid():
    return str(uuid4())


@register.filter
def list_item(lst, i):
    try:
        return lst[i]
    except:
        return None


# @register.simple_tag(takes_context=True, name='nformat')
# def nformat(context, number, locale=None):
#     if locale is None:
#         locale = to_locale(get_language())
#     return format_decimal(float(number), format="#,##0.00", locale=locale)


@register.filter(takes_context=True, name='nformat')
def nformat(number, format=None):
    if not number:
        return None
    locale = to_locale(get_language())
    return format_decimal(number, format=format or "#,##0.00", locale=locale)


@register.filter
def plus_days(value, days):
    return value + datetime.timedelta(days=days)


@register.filter
def minus_days(value, days):
    return value - datetime.timedelta(days=days)


@register.filter()
def addDays(days):
    return datetime.date.today() + datetime.timedelta(days=days)


@register.filter(name='dict_first_key')
def dict_first_key(d):
    '''Returns the given key from a dictionary.'''
    return next(iter(d))[0]


@register.filter(name='dict_first_value')
def dict_first_value(d):
    '''Returns the given key from a dictionary.'''
    return next(iter(d))[1]
