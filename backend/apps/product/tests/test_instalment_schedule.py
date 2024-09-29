from datetime import datetime

import pytest

from apps.product.instalment_schedule import INSTALMENT_CAPITAL_SELECTOR, INSTALMENT_TOTAL_SELECTOR, \
    INSTALMENT_INTEREST_SELECTOR, INSTALMENT_MATURITY_DATE_SELECTOR
from apps.product.instalment_schedule.instalment_schedule import InstalmentSchedule
from apps.product.models import ProductCalculation
from utils.utils import add_month

custom_instalment_schedule = [
    {
        'maturityDate': {'value': "2024-09-02"},
        'instalmentTotal': {'value': 2300},
    },
    {
        'maturityDate': {'value': "2024-10-01"},
        'instalmentTotal': {'value': 2300},
    },
    {
        'maturityDate': {'value': "2024-11-01"},
        'instalmentTotal': {'value': 2950, 'change_flag': 1},
    },
    {
        'maturityDate': {'value': "2024-12-02"},
        'instalmentTotal': {'value': 2300},
    },
    {
        'maturityDate': {'value': "2025-01-01"},
        'instalmentTotal': {'value': 2300},
    },
    {
        'maturityDate': {'value': "2025-02-03"},
        'instalmentTotal': {'value': 2300},
    },
    {
        'maturityDate': {'value': "2025-03-03"},
        'instalmentTotal': {'value': 2300},
    },
    {
        'maturityDate': {'value': "2025-04-01"},
        'instalmentTotal': {'value': 2300},
    },
    {
        'maturityDate': {'value': "2025-05-01"},
        'instalmentTotal': {'value': 2300},
    },
    {
        'maturityDate': {'value': "2025-06-02"},
        'instalmentTotal': {'value': 2300},
    },
    {
        'maturityDate': {'value': "2025-07-01"},
        'instalmentTotal': {'value': 2300},
    },
    {
        'maturityDate': {'value': "2025-08-01"},
        'instalmentTotal': {'value': 227300.64},
    }
]


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
    def test_calculate_instalment_interest(self, fix_user, fix_product, fix_product_calculation):
        instalment_schedule = InstalmentSchedule(
            user=fix_user,
            product=fix_product,
            balance=100000,
            interest_rate=.11
        )

        instalment_interest = instalment_schedule.calculate_instalment_interest(
            start_date=datetime(2024, 9, 15).date(),
            end_date=datetime(2024, 9, 30).date(),
        )

        assert round(instalment_interest, 4) == 285.71

        # instalment_interest = instalment_schedule.calculate_instalment_interest(
        #     start_date=datetime(2024, 9, 15).date(),
        #     end_date=datetime(2024, 9, 30).date(),
        #     product_in_default=True
        # )
        #
        # assert round(instalment_interest, 4) == 480.5178

    def test_instalment_schedule_product(self, fix_user, fix_product, fix_product_calculation):
        instalment_list = InstalmentSchedule(
            user=fix_user,
            product=fix_product,
            balance=None,
            interest_rate=.09,
            instalment_rate=None,
            instalment_constant_value=4500,
            instalment_schedule=None,
            instalment_number=None,
            start_date=None
        ).calculate

        assert instalment_list

    def test_instalment_schedule_no_product_start_date(self, fix_user):
        dt = datetime.strptime('2024-09-15', '%Y-%m-%d').date()

        instalment_list = InstalmentSchedule(
            user=fix_user,
            balance=100000,
            interest_rate=.09,
            instalment_rate=None,
            instalment_constant_value=4500,
            instalment_schedule=None,
            instalment_number=12,
            start_date=dt).calculate

        assert len(instalment_list['sections']) == 12
        assert instalment_list['sections'][0][INSTALMENT_MATURITY_DATE_SELECTOR] == add_month(dt, 1)

    def test_instalment_schedule_no_product_no_start_date_constant_value(self, fix_user):
        balance = 150236

        instalment_list = InstalmentSchedule(
            user=fix_user,
            balance=balance,
            interest_rate=.09,
            instalment_rate=None,
            instalment_constant_value=4500,
            instalment_schedule=None,
            instalment_number=12,
            start_date=None
        ).calculate

        capital = 0

        for i in instalment_list['sections']:
            capital += i[INSTALMENT_CAPITAL_SELECTOR]

        assert round(capital, 2) == balance

    def test_instalment_schedule_no_product_no_start_date_instalment_rate(self, fix_user):
        balance = 2360228

        instalment_list = InstalmentSchedule(
            user=fix_user,
            balance=balance,
            interest_rate=.09,
            instalment_rate=.01,
            instalment_constant_value=None,
            instalment_schedule=None,
            instalment_number=12,
            start_date=None
        ).calculate

        capital = 0

        for i in instalment_list['sections']:
            capital += i[INSTALMENT_CAPITAL_SELECTOR]

        assert round(capital, 2) == balance

    def test_instalment_schedule_no_product_custom_instalment_schedule_instalment_rate(self, fix_user):
        instalment_number = len(custom_instalment_schedule)
        balance = 100000

        instalment_list = InstalmentSchedule(
            user=fix_user,
            balance=balance,
            interest_rate=.09,
            instalment_rate=.01,
            instalment_constant_value=None,
            instalment_schedule=custom_instalment_schedule,
            instalment_number=None,
            start_date=None
        ).calculate

        assert instalment_number == len(instalment_list['sections'])

        capital = 0

        for i in instalment_list['sections']:
            capital += i[INSTALMENT_CAPITAL_SELECTOR]

        assert round(capital, 2) == balance

    def test_instalment_schedule_no_product_custom_instalment_schedule_instalment_constant_value(self, fix_user):
        balance = 100000

        instalment_list = InstalmentSchedule(
            user=fix_user,
            balance=balance,
            interest_rate=.09,
            instalment_rate=None,
            instalment_constant_value=2200,
            instalment_schedule=custom_instalment_schedule,
            instalment_number=None,
            start_date=None
        ).calculate

        capital = 0

        for i in instalment_list['sections']:
            capital += i[INSTALMENT_CAPITAL_SELECTOR]

        assert round(capital, 2) == balance

    def test_instalment_schedule_no_product_custom_instalment_schedule_change_flag(self, fix_user):
        instalment_number = len(custom_instalment_schedule)
        balance = 100000

        instalment_list = InstalmentSchedule(
            user=fix_user,
            balance=balance,
            interest_rate=.09,
            instalment_rate=None,
            instalment_constant_value=2300,
            instalment_schedule=custom_instalment_schedule,
            instalment_number=None,
            start_date=None
        ).calculate

        assert instalment_number == len(instalment_list['sections'])
        assert instalment_list['sections'][1][INSTALMENT_TOTAL_SELECTOR] == 2300
        assert instalment_list['sections'][2][INSTALMENT_TOTAL_SELECTOR] == 2950

    def test_instalment_schedule_no_product_no_interest_rate_constant_value(self, fix_user):
        balance = 100000

        instalment_list = InstalmentSchedule(
            user=fix_user,
            balance=balance,
            interest_rate=None,
            instalment_rate=None,
            instalment_constant_value=2300,
            instalment_schedule=custom_instalment_schedule,
            instalment_number=None,
            start_date=None
        ).calculate

        for i in instalment_list['sections']:
            assert i[INSTALMENT_INTEREST_SELECTOR] == 0
