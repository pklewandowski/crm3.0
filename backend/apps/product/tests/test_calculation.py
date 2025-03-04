import datetime

import pytest

from apps.document.models import DocumentTypeAccountingType
from apps.product.calc import LoanCalculation
from apps.product.models import ProductCashFlow
from conftest import fix_user


@pytest.fixture
def fix_product_cashflow(fix_product):
    cf = [
        {
            "pk": 16061,
            "product": fix_product,
            "transaction_uid": None,
            "type": DocumentTypeAccountingType.objects.get(pk=2),
            "subtype": "",
            "value": 4500.00,
            "cash_flow_date": "2024-01-19",
            "accounting_date": None,
            "entry_source": "HAND",
            "description": "I rata",
            "editable": True,
            "calculable": True
        },
        {
            "pk": 16062,
            "product": fix_product,
            "transaction_uid": None,
            "type": DocumentTypeAccountingType.objects.get(pk=2),
            "subtype": "",
            "value": 4500.00,
            "cash_flow_date": "2024-02-19",
            "accounting_date": None,
            "entry_source": "HAND",
            "description": "II rata",
            "editable": True,
            "calculable": True
        },
    ]

    for i in cf:
        ProductCashFlow.objects.create(**i)


@pytest.mark.django_db
class TestCalculation:
    def test_product_calculation(self, fix_product, fix_user):
        calculate_list = LoanCalculation(product=fix_product, user=fix_user).calculate()
        assert True

    def test_product_calculation_simulation_emulate(self, fix_product, fix_user, fix_product_cashflow):
        calculate_list = LoanCalculation(
            product=fix_product, user=fix_user
        ).calculate(
            end_date=datetime.datetime.strptime('2025-03-12', '%Y-%m-%d').date(),
            simulation=True,
            emulate_payment=True
        )
        assert True

    def test_product_calculation_simulation_no_emulate(self, fix_product, fix_user, fix_product_cashflow):
        calculate_list = LoanCalculation(
            product=fix_product, user=fix_user
        ).calculate(
            end_date=datetime.datetime.strptime('2025-03-12', '%Y-%m-%d').date(),
            simulation=True
        )
        assert True
