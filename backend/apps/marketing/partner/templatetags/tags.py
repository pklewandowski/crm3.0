from django import template
from ..models import PartnerSecurityType

register = template.Library()


# @register.simple_tag(name='get_medium')
# def get_medium(v):
#     if not v:
#         return
#     try:
#         return Medium.objects.get(pk=v).name
#     except Medium.DoesNotExist:
#         return v
#
#
# @register.simple_tag(name='get_source')
# def get_source(v):
#     if not v:
#         return
#     try:
#         return Source.objects.get(pk=v).name
#     except Source.DoesNotExist:
#         return v


@register.simple_tag(name='get_security_type')
def get_security_type(v):
    if not v:
        return
    try:
        return PartnerSecurityType.objects.get(pk=v).name
    except PartnerSecurityType.DoesNotExist:
        return v
