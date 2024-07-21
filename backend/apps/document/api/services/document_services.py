from apps.document.models import DocumentTypeAttributeFeature, DocumentTypeAttribute


def get_ver(document_type, status):
    return {
        str(i.attribute.pk): {"V": i.visible, "E": i.editable, "R": i.required}
        for i in DocumentTypeAttributeFeature.objects.filter(
            attribute__in=DocumentTypeAttribute.objects.filter(document_type=document_type),
            status=status
        )
    }
