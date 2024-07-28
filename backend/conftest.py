import datetime

import pytest
from django.db import connection
from django.db.models.signals import pre_migrate
from django.dispatch import receiver

from apps.document.models import DocumentType, DocumentTypeCategory, DocumentTypeProcessFlow
from apps.product.models import ProductInterestGlobal
from apps.user.models import User
from crm import settings


# @pytest.fixture(scope='session', autouse=True)
# def django_db_setup():
#     settings.DATABASES['default'] = {
#         'ENGINE': 'django.db.backends.postgresql',
#         'OPTIONS': {'options': '-c search_path=crm'},
#         'NAME': 'crm_test',
#         'USER': 'crm_test',
#         'PASSWORD': 'crm_test',
#         'HOST': '127.0.0.1',
#         'PORT': '5432',
#         'DATABASE_SCHEMA': 'crm'
#     }

# # allow perform tests without using @pytest.mark.django_db
# @pytest.fixture(autouse=True)
# def enable_db_access_for_all_tests(db):
#     pass

@receiver(pre_migrate)
def create_schema(sender, **kwargs) -> None:
    with connection.cursor() as cursor:
        cursor.execute("CREATE SCHEMA IF NOT EXISTS crm;")


@pytest.fixture(autouse=True)
def db_data():
    user = User.objects.create_superuser('admin', 'admin@3ws.pl', 'password')
    document_category = DocumentTypeCategory.objects.create(
        name='LOAN_CATEGORY',
        code='LOAN_1',
        sq=1
    )

    document_type = DocumentType.objects.create(
        name='TEST_LOAN',
        category=document_category,
        is_process_flow=True,
        is_product=True,
        is_shadow=True,
        is_code=True,
        is_owner=False,
        is_code_editable=False
    )


@pytest.fixture(autouse=True)
def user():
    return User.objects.get(username='admin')


@pytest.fixture(autouse=True)
def document_type():
    return DocumentType.objects.get(name='TEST_LOAN')
