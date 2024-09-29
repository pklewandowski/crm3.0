import pytest

from apps.document.models import DocumentTypeCategory, DocumentType
from apps.user_func.client.models import Client


@pytest.fixture
def fix_client_category():
    return DocumentTypeCategory.objects.create(
        name='Zasoby ludzkie',
        code='HR',
        sq=1
    )


@pytest.fixture
def fix_client_document_type(fix_client_category):
    return DocumentType.objects.create(
        name='Client',
        category=fix_client_category,
        is_process_flow=True,
        is_product=True,
        is_shadow=True,
        is_code=True,
        is_owner=False,
        is_code_editable=False
    )


@pytest.fixture
def fix_client(fix_user, fix_client_document_type):
    return Client.objects.create(
        user=fix_user,
        status='IN',
        document_type=fix_client_document_type
    )
