import pytest

from apps.document.models import Document, DocumentTypeStatus, DocumentType, DocumentTypeCategory, \
    DocumentTypeAccounting


@pytest.fixture
def fix_document_category():
    return DocumentTypeCategory.objects.create(
        name='LOAN_CATEGORY',
        code='LOAN_1',
        sq=1
    )


@pytest.fixture
def fix_document_type(fix_document_category):
    return DocumentType.objects.create(
        name='TEST_LOAN',
        category=fix_document_category,
        is_process_flow=True,
        is_product=True,
        is_shadow=True,
        is_code=True,
        is_owner=False,
        is_code_editable=False
    )


@pytest.fixture
def fix_document_status(fix_document_type):
    return DocumentTypeStatus.objects.create(**{
        "name": "Kompletowanie wniosku",
        "code": "NW",
        "is_initial": True,
        "type": fix_document_type,
        "permission": "loan_application_add",
        "is_product": False,
        "sq": 1,
        "is_active": True,
        "is_alternate": False,
        "is_required_validation": True,
        "can_revert": True,
        "is_closing_process": False,
        "color": "ffffff"
    })


@pytest.fixture
def fix_document(fix_user, fix_document_status, fix_document_type):
    return Document.objects.create(
        created_by=fix_user,
        type=fix_document_type,
        status=fix_document_status,
        owner=fix_user,
        code="1/2024",
    )

# @pytest.fixture
# def fix_document_type_accounting():
#     DocumentTypeAccounting.objects.create(**{
#
#     "sq": 1,
#     "id_document_type": 26,
#     "id_accounting_type": 5
#   },
#   {"sq": 2,
#     "id_document_type": 26,
#     "id_accounting_type": 11
#   },
#   {
#     "id": 232,
#     "sq": 3,
#     "id_document_type": 26,
#     "id_accounting_type": 9
#   },
#   {
#
#     "sq": 4,
#     "id_document_type": 26,
#     "id_accounting_type": 3
#   },
#   {
#     "id": 234,
#     "sq": 5,
#     "id_document_type": 26,
#     "id_accounting_type": 1
#   },
#   {
#
#     "sq": 6,
#     "id_document_type": 26,
#     "id_accounting_type": 4
#   },
#   {
#
#     "sq": 0,
#     "id_document_type": 26,
#     "id_accounting_type": 7
#   },
#   {
#
#     "sq": 0,
#     "id_document_type": 26,
#     "id_accounting_type": 16
#   },
#   {
#
#     "sq": 0,
#     "id_document_type": 26,
#     "id_accounting_type": 17
#   },
#   {
#
#     "sq": 0,
#     "id_document_type": 26,
#     "id_accounting_type": 18
#   },
#   {
#
#     "sq": 0,
#     "id_document_type": 26,
#     "id_accounting_type": 19
#   },
#   {
#
#     "sq": 0,
#     "id_document_type": 26,
#     "id_accounting_type": 20
#   },
#   {
#
#     "sq": 0,
#     "id_document_type": 26,
#     "id_accounting_type": 2
#   }
#
#     )