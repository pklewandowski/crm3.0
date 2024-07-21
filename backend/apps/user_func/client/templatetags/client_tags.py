from django import template
from apps.user_func.client.models import Client

register = template.Library()


@register.filter(name='get_status_label')
def get_status_label(v):
    if isinstance(v, Client):
        return v.get_status_label()
    else:
        return ''


@register.filter(name='get_status_label')
def get_source_label(v):
    if isinstance(v, Client):
        return v.get_source_label()
    else:
        return ''

