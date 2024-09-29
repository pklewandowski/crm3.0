import datetime
from django import template
from django.db.models import Q

from apps.product.models import ProductCalculation
from apps.document.models import DocumentTypeAttributeFeature, DocumentTypeAttribute, DocumentTypeSection, DocumentTypeStatus

register = template.Library()


@register.filter(name='product_calculation')
def product_calculation(product):
    try:
        if product:
            return product.calculation.get(product=product, calc_date=datetime.date.today() - datetime.timedelta(days=1))
    except ProductCalculation.DoesNotExist:
        return None
    return None


@register.filter(name='is_section_empty')
def is_section_empty(section, status):
    if not section or not status:
        return False

    q = Q(section=section) | Q(section__in=section.children.all())

    visible = DocumentTypeAttributeFeature.objects.filter(
        status=status,
        visible=True,
        attribute__in=DocumentTypeAttribute.objects.filter(q)
    ).count()

    return True if visible == 0 else False
