from django import template

from apps.product.view.views import _count_balance

register = template.Library()


@register.filter(name='get_cashflow_sum')
def get_cashflow_sum(cashflow_list, type_code):
    try:
        val = 0

        for i in cashflow_list:
            if i.instance:
                if i.instance.type.code == type_code:
                    val += i.instance.value
        return val
    except:
        return None


@register.filter(name='count_balance')
def count_balance(product):
    return _count_balance(product)['balance']


@register.filter(name='split_decimal')
def split_decimal(val):
    if not val:
        return None
    return str(val).split('.')
