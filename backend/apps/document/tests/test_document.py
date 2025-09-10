import pytest

from apps.document.api.attribute_utils import AttributeUtils
from apps.document.api.views import AttributeModel
from apps.document.models import DocumentTypeAccountingType, DocumentType


@pytest.mark.django_db
class TestDocument:
    def test_get_accounting_types(self):
        acc_types = DocumentTypeAccountingType.get_accounting_types(DocumentType.objects.get(pk=24))


@pytest.mark.django_db
def test_get_VER(fix_document_type):
    attributes = []

    AttributeUtils.get_attributes(
        parent=None,
        document_type=DocumentType.objects.get(pk=1),
        level=attributes,
        type=None,
        status=None
    )

    result = AttributeModel._get_VER(attributes, None, True)

    pass
