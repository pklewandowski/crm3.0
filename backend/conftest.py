import pytest
from django.db import connection
from django.db.models.signals import pre_migrate
from django.dispatch import receiver

from apps.document.models import DocumentType
from apps.user.models import User

pytest_plugins = [
    "apps.document.tests.fixtures",
    "apps.product.tests.fixtures",
    "apps.user_func.client.tests.fixtures"
]

@receiver(pre_migrate)
def create_schema(sender, **kwargs) -> None:
    with connection.cursor() as cursor:
        cursor.execute("CREATE SCHEMA IF NOT EXISTS crm;")

@pytest.fixture(autouse=True)
def fix_system_user():
    return User.objects.create(
            **{
                "last_name": "__systemprocess",
                "password": "pbkdf2_sha256$150000$C4nYM6wNxpWS$YzjvAo7Hi0i9MWRX5QetoNdJwt8n66gunpOkZgorWBY=",
                "password_valid": False,
                "is_superuser": True,
                "is_staff": True,
                "is_active": False,
                "date_joined": "2000-01-01",
                "username": "__systemprocess",
                "ldap": False,
                "sex": "X",
                "status": "SYSTEM"
            }
    )

@pytest.fixture(autouse=True)
def fix_user():
    return User.objects.create_superuser('admin', 'admin@3ws.pl', 'password')

