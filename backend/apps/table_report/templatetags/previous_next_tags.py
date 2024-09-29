import datetime

from django import template

register = template.Library()


@register.filter(name='next_item')
def next_item(some_list, current_index):
    """
    Returns the next element of the list using the current index if it exists.
    Otherwise returns an empty string.
    """
    try:
        return some_list[int(current_index) + 1]  # access the next element
    except:
        return ''  # return empty string in case of exception


@register.filter(name='previous_item')
def previous_item(some_list, current_index):
    """
    Returns the previous element of the list using the current index if it exists.
    Otherwise returns an empty string.
    """
    try:
        return some_list[int(current_index) - 1]  # access the previous element
    except:
        return ''  # return empty string in case of exception


@register.filter(name='get_object_attr')
def get_object_attr(obj, property_name):
    if not obj:
        return ''
    attr = getattr(obj, property_name)
    return attr


@register.filter(name='datediffdays')
def datediffdays(date1, date2):
    if not date1:
        return ''
    if not date2:
        date2 = datetime.datetime.now()

    return (date2 - date1).days
