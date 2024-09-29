
from apps.document.models import DocumentTypeAttributeFeature


def get_field_name(attribute, section, status_code, feature):
    return "%s_%s_%s_%s" % (str(attribute.pk), str(section.pk), status_code, feature)


def get_attribute_features(document_type, status, readonly=False):
    return {i.attribute.pk: {'visible': i.visible, 'editable': i.editable if not readonly else False, 'required': i.required}
            for i in DocumentTypeAttributeFeature.objects.filter(attribute__document_type=document_type, status=status).prefetch_related('attribute')}
