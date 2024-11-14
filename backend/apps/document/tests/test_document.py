import pytest

from apps.document.models import DocumentTypeAccountingType, DocumentType

@pytest.mark.django_db
class TestDocument:
    def test_get_accounting_types(self):
        acc_types = DocumentTypeAccountingType.get_accounting_types(DocumentType.objects.get(pk=24))
