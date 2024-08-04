import datetime

from apps.product.calc import CalculateLoan
from apps.product.models import Product
from apps.user.models import User


class InstalmentSchedule:
    def __init__(self, user: User, product: Product = None):
        self.user = user
        self.product = product

    def _calculate_instalment(self):
        pass

    def __call__(
            self,
            balance_value,
            interest_rate,
            instalment_percent: float = None,
            instalment_constant_value: float = None,
            instalment_schedule: list = None,
            instalment_count: int = None,
            start_date: datetime.date = None) -> dict:

        if start_date >= datetime.date.today():
            raise ValueError("start_date must be in the past")

        if not instalment_percent and not instalment_constant_value:
            raise ValueError("instalment_percent or instalment_constant_value must not be empty")

        state = self._get_state(dt=start_date)
        day_interval = 0

        if self.product:
            instalment_schedule = self.product.schedule_set.filter(maturity_date__gte=start_date).order_by(
                'maturity_date')

        if not self.product and not instalment_schedule:
            day_interval = 30

        if state:
            balance = state['balance']
            interest_rate = state['interest_rate']
            interest_required_total = state['interest_required_total']
        else:
            balance = balance_value
            interest_rate = interest_rate
            interest_required_total = 0

        for i in range(instalment_count) if instalment_count else instalment_schedule:
            pass

        return {}

    def _get_state(self, dt=datetime.date.today(), run_calculation=True):
        if not self.product:
            return None

        calculation = self.product.calculation.filter(calc_date=dt)

        if not calculation:
            if run_calculation:
                CalculateLoan(product=self.product, user=self.user).calculate()

        calculation = self.product.calculation.filter(calc_date=dt)

        if not calculation:
            raise ValueError("No calculation found")

        return {
            'balance': calculation.capital_not_required + calculation.capital_required,
            'interest_rate': calculation.interest_rate,
            'interest_required_total': calculation.interest_per_day + calculation.interest_for_delay_required_daily
        }
