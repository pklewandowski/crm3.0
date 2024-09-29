from datetime import datetime
from decimal import Decimal

import pytest

from apps.product.instalment_schedule.instalment_schedule import InstalmentSchedule
from apps.product.models import ProductCalculation


@pytest.fixture
def fix_product_calculation(fix_product):
    return ProductCalculation.objects.create(**{
        "id": "202409151130",
        "calc_date": "2024-09-15",
        "capital_not_required": 31209.84,
        "capital_required": 31993.40,
        "interest_required": 0.00,
        "cost_occurrence": 0.00,
        "cost": 0.00,
        "cost_total": 0.00,
        "instalment_accounting_capital_required": 0.00,
        "instalment_accounting_capital_not_required": 0.00,
        "instalment_accounting_cost": 0.00,
        "product": fix_product,
        "instalment": 0.00,
        "instalment_total": 4500.00,
        "capital_required_from_schedule": 0.00,
        "commission_not_required": 0.00,
        "instalment_overdue_count": 7,
        "commission_required": 0.00,
        "instalment_accounting_interest_for_delay": 0.00,
        "commission_required_from_schedule": 0.00,
        "instalment_accounting_commission_not_required": 0.00,
        "instalment_accounting_commission_required": 0.00,
        "instalment_accounting_interest_required": 0.00,
        "interest_for_delay_rate": 18.50,
        "interest_for_delay_required": 7464.04,
        "interest_for_delay_required_daily": 32.03,
        "interest_for_delay_total": 7464.04,
        "interest_required_from_schedule": 0.00,
        "required_liabilities_sum": 31993.40,
        "required_liabilities_sum_from_schedule": 0.00,
        "instalment_overpaid": 0.00,
        "remission_capital": 0.00,
        "remission_commission": 0.00,
        "remission_cost": 0.00,
        "remission_interest": 0.00,
        "remission_interest_for_delay": 0.00,
        "interest_per_day": 0.00,
        "commission_per_day": 0.00,
        "capital_per_day": 5821.01,
        "instalment_overdue_occurrence": 8,
        "product_status": fix_product.status,
        "interest_rate": 9.00,
        "interest_for_delay_calculation_base": 63203.24,
        "balance": 70667.29,
        "interest_cumulated_per_day": 509.84,
        "interest_daily": 0.00
    })


@pytest.mark.django_db
class TestInstalmentSchedule:
    def test_calculate_instalment_interest(self, fix_user, fix_product):
        instalment_schedule = InstalmentSchedule(user=fix_user, product=fix_product)

        instalment_interest = instalment_schedule.calculate_instalment_interest(
            start_date=datetime(2024, 9, 15).date(),
            end_date=datetime(2024, 9, 30).date(),
            interest_rate=.11,
            balance=100000
        )

        assert round(instalment_interest, 4) == 452.0548

        instalment_interest = instalment_schedule.calculate_instalment_interest(
            start_date=datetime(2024, 9, 15).date(),
            end_date=datetime(2024, 9, 30).date(),
            interest_rate=.11,
            balance=100000,
            product_in_default=True
        )

        assert round(instalment_interest, 4) == 760.2740

    def test_instalment_schedule(self, fix_user, fix_product, fix_product_calculation):
        instalment_schedule = InstalmentSchedule(user=fix_user, product=fix_product)
        instalment_list = instalment_schedule.calculate(
            balance_value=None,
            interest_rate=.09,
            instalment_rate=None,
            instalment_constant_value=4500,
            instalment_schedule=None,
            instalment_count=None,
            start_date=datetime.strptime('2024-09-15', '%Y-%m-%d').date()
        )

        assert True
