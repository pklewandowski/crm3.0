import datetime
from decimal import Decimal

from apps.product.calc import CalculateLoan
from apps.product.models import Product, ProductCalculation, ProductInterestGlobal
from apps.user.models import User


class InstalmentSchedule:
    def __init__(self, user: User, product: Product = None):
        self.user = user
        self.product = product
        self.constant_interval = 30 if not self.product else None

    def _calculate_instalment(
            self,
            balance,
            interest_rate,
            instalment_rate,
            instalment_constant_value,
            current_date,
            due_date,
            baloon):

        balance = round(float(balance), 4)

        dt_int = self._get_date_interval(current_date, due_date)
        instalment_interest = round(balance * interest_rate / 365 * dt_int, 4)

        if baloon:
            return {
                'due_date': due_date,
                'instalment_capital': balance,
                'instalment_interest': instalment_interest,
                'instalment_total': balance + instalment_interest
            }

        if instalment_constant_value:
            instalment_capital = max(0, instalment_constant_value - instalment_interest)
            instalment_interest = min(instalment_interest, instalment_constant_value)
        else:
            instalment_capital = round(balance * instalment_rate, 4)

        return {
            'due_date': due_date,
            'instalment_capital': instalment_capital,
            'instalment_interest': instalment_interest,
            'instalment_total': instalment_capital + instalment_interest
        }

    def _get_date_interval(self, current_date: datetime.date = None, next_due_date: datetime.date = None) -> int:
        if self.constant_interval:
            return self.constant_interval
        else:
            if current_date is None or next_due_date is None:
                raise ValueError("current_date and due_date must be set")

            return abs((current_date - next_due_date).days)

    def calculate_instalment_interest(
            self,
            start_date: datetime.date,
            end_date: datetime.date,
            interest_rate: float,
            balance: float,
            product_in_default: bool = False
    ):
        instalment_interest = 0

        days = self._get_date_interval(current_date=start_date, next_due_date=end_date)

        if not product_in_default:
            return float(balance * interest_rate / 365 * days)

        for i in range(abs(start_date - end_date).days):
            interest_for_delay = ProductInterestGlobal.get_for(date=start_date + datetime.timedelta(days=i))
            instalment_interest += balance * interest_for_delay[0] / 365

        return float(instalment_interest)

    def calculate(
            self,
            balance_value,
            interest_rate,
            instalment_rate: float = None,
            instalment_constant_value: float = None,
            instalment_schedule: list = None,
            instalment_count: int = None,
            start_date: datetime.date = None) -> dict:

        if start_date and start_date >= datetime.date.today():
            raise ValueError("start_date must be in the past")

        if not self.product and not instalment_schedule and not instalment_rate and not instalment_constant_value:
            raise ValueError(
                "when no product, instalment_schedule, instalment_percent or instalment_constant_value must not be empty")

        instalment_list = []
        instalment_capital_total = 0.0
        instalment_interest_total = 0.0

        if self.product:
            state = self._get_state()
            instalment_schedule = self.product.schedule_set.filter(
                maturity_date__gte=start_date).order_by('maturity_date')
            current_date = state['calc_date']
            balance = float(state['balance'])
            interest_required_total = state['interest_required_total']
        else:
            balance = float(balance_value)
            interest_required_total = 0
            current_date = start_date

        for idx, i in enumerate(range(instalment_count)) if instalment_count else enumerate(instalment_schedule):
            due_date = i.maturity_date if instalment_schedule else None

            instalment = self._calculate_instalment(
                balance=balance,
                interest_rate=interest_rate,
                instalment_rate=instalment_rate,
                instalment_constant_value=instalment_constant_value,
                current_date=current_date,
                due_date=due_date,
                baloon=idx == len(instalment_schedule) - 1 if instalment_schedule else i
            )
            if not idx:
                instalment['instalment_interest'] += float(interest_required_total)

            balance -= instalment['instalment_capital']

            instalment_list.append(instalment)

            instalment_capital_total += instalment['instalment_capital']
            instalment_interest_total += instalment['instalment_interest']

            current_date = i.maturity_date if instalment_schedule else None

        return {
            'list': instalment_list,
            'capital_total': instalment_capital_total,
            'interest_total': instalment_interest_total
        }

    def _get_state(self, run_calculation=False):
        if not self.product:
            return None

        if run_calculation:
            CalculateLoan(product=self.product, user=self.user).calculate()

        calculation = self.product.calculation.all().order_by('calc_date').last()

        if not calculation:
            raise Exception("No calculation found")

        return {
            'calc_date': calculation.calc_date,
            'balance': calculation.capital_not_required + calculation.capital_required,
            'interest_rate': calculation.interest_rate,
            'interest_required_total': calculation.interest_per_day + calculation.interest_for_delay_required_daily
        }
