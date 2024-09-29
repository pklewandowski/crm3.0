import datetime

from apps.product.api.instalment_schedule.views import ProductInstalmentScheduleView
from apps.product.instalment_schedule import INSTALMENT_MATURITY_DATE_SELECTOR, INSTALMENT_CAPITAL_SELECTOR, \
    INSTALMENT_COMMISSION_SELECTOR, INSTALMENT_TOTAL_SELECTOR, INSTALMENT_INTEREST_SELECTOR, \
    INSTALMENT_CONSTANT_DAYS_INTERVAL
from apps.product.calc import CalculateLoan
from apps.product.models import Product, ProductInterestGlobal, ProductSchedule
from apps.user.models import User
from utils.utils import add_month


class InstalmentSchedule:
    def __init__(self, user: User, product: Product = None):
        self.user = user
        self.product = product

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
        instalment_interest = round(balance * interest_rate / 365 * dt_int, 4) if interest_rate else 0

        if baloon:
            return {
                INSTALMENT_MATURITY_DATE_SELECTOR: due_date,
                INSTALMENT_CAPITAL_SELECTOR: round(balance, 4),
                INSTALMENT_COMMISSION_SELECTOR: 0.0,
                INSTALMENT_INTEREST_SELECTOR: round(instalment_interest, 4),
                INSTALMENT_TOTAL_SELECTOR: round(balance + instalment_interest, 4),
                'days': dt_int
            }

        if instalment_constant_value:
            instalment_capital = max(0, instalment_constant_value - instalment_interest)
            instalment_interest = min(instalment_interest, instalment_constant_value)
        else:
            instalment_capital = round(balance * instalment_rate, 4)

        return {
            INSTALMENT_MATURITY_DATE_SELECTOR: due_date,
            INSTALMENT_CAPITAL_SELECTOR: round(instalment_capital, 4),
            INSTALMENT_COMMISSION_SELECTOR: 0.0,
            INSTALMENT_INTEREST_SELECTOR: round(instalment_interest, 4),
            INSTALMENT_TOTAL_SELECTOR: round(instalment_capital + instalment_interest, 4),
            'days': dt_int
        }

    def _get_date_interval(self, current_date: datetime.date = None, next_due_date: datetime.date = None) -> int:
        if current_date is None or next_due_date is None:
            return INSTALMENT_CONSTANT_DAYS_INTERVAL
        elif current_date:
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

    def _calculate_due_date(self, due_date: datetime.date) -> datetime.date | None:
        if not due_date:
            return None

        weekday = due_date.weekday()
        delta = 7 - weekday if weekday > 4 else 0

        return due_date + datetime.timedelta(days=delta)

    def _get_due_date(self, current_date: datetime.date) -> datetime.date | None:
        if not current_date:
            return None

        due_date = add_month(current_date, 1)
        return self._calculate_due_date(due_date)

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

    def _get_instalment_schedule_maturity_date(self, instalment_schedule_item):
        if isinstance(instalment_schedule_item, ProductSchedule):
            return self._calculate_due_date(instalment_schedule_item.maturity_date)

        if type(instalment_schedule_item) == dict:
            return self._calculate_due_date(
                datetime.datetime.strptime(instalment_schedule_item['maturityDate']['value'], '%Y-%m-%d').date()
            )

        raise Exception("Invalid instalment schedule item type")

    def _get_instalment_schedule_total(self, instalment_schedule_item):
        if isinstance(instalment_schedule_item, ProductSchedule):
            return {
                'value': instalment_schedule_item.instalment_total,
                'change_flag': None
            }

        if type(instalment_schedule_item) == dict:
            return instalment_schedule_item['instalmentTotal']

        raise Exception("Invalid instalment schedule item type")

    def calculate(
            self,
            balance_value,
            interest_rate: float = 0,
            instalment_rate: float = None,
            instalment_constant_value: float = None,
            instalment_schedule: list = None,
            instalment_count: int = None,
            start_date: datetime.date = None) -> dict:

        instalment_list = []
        instalment_capital_total = 0.0
        instalment_interest_total = 0.0
        instalment_value_total = 0.0

        if not self.product:
            if not instalment_count and not instalment_schedule:
                raise Exception("No instalment count / schedule found")

            if not instalment_schedule and not instalment_rate and not instalment_constant_value:
                raise ValueError(
                    "when no product, instalment_schedule, instalment_percent or instalment_constant_value must not be empty")

            balance = float(balance_value)
            interest_required_total = 0
            current_date = start_date

        else:
            state = self._get_state()
            assert state

            start_date = state['calc_date']
            instalment_schedule = self.product.schedule_set.filter(
                maturity_date__gte=start_date).order_by('maturity_date')

            current_date = state['calc_date']
            balance = float(state['balance'])
            interest_required_total = state['interest_required_total']

        for idx, i in enumerate(range(instalment_count)) if instalment_count else enumerate(instalment_schedule):
            due_date = self._calculate_due_date(
                self._get_instalment_schedule_maturity_date(i)) if instalment_schedule else self._get_due_date(
                current_date)

            _instalment_constant_value = instalment_constant_value

            if instalment_schedule:
                instalment_total = self._get_instalment_schedule_total(i)
                _instalment_constant_value = instalment_constant_value if not 'change_flag' in instalment_total or \
                                                                          instalment_total['change_flag'] is None else \
                    instalment_total['value']

            instalment = self._calculate_instalment(
                balance=balance,
                interest_rate=interest_rate,
                instalment_rate=instalment_rate,
                instalment_constant_value=_instalment_constant_value,
                current_date=current_date,
                due_date=due_date,
                baloon=idx == len(instalment_schedule) - 1 if instalment_schedule else i == instalment_count - 1
            )
            if not idx:
                instalment[INSTALMENT_INTEREST_SELECTOR] += float(interest_required_total)

            balance -= instalment[INSTALMENT_CAPITAL_SELECTOR]

            instalment_list.append(instalment)

            instalment_capital_total += instalment[INSTALMENT_CAPITAL_SELECTOR]
            instalment_interest_total += instalment[INSTALMENT_INTEREST_SELECTOR]
            instalment_value_total += instalment[INSTALMENT_TOTAL_SELECTOR]

            current_date = due_date

        return {
            'list': instalment_list,
            'aggregates': {
                'capital_total': instalment_capital_total,
                'interest_total': instalment_interest_total,
                'instalment_total': instalment_value_total
            }
        }
