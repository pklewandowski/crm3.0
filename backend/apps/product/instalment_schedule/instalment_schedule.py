import datetime

from django.conf import settings

from apps.product.calc import CalculateLoan
from apps.product.instalment_schedule import INSTALMENT_MATURITY_DATE_SELECTOR, INSTALMENT_CAPITAL_SELECTOR, \
    INSTALMENT_COMMISSION_SELECTOR, INSTALMENT_TOTAL_SELECTOR, INSTALMENT_INTEREST_SELECTOR, \
    INSTALMENT_CONSTANT_DAYS_INTERVAL, INSTALMENT_CAPITAL_AGGREGATE, INSTALMENT_INTEREST_AGGREGATE, \
    INSTALMENT_COMMISSION_AGGREGATE, INSTALMENT_TOTAL_AGGREGATE
from apps.product.models import Product, ProductInterestGlobal, ProductSchedule
from apps.user.models import User
from utils.utils import add_month


class InstalmentSchedule:
    def __init__(
            self,
            user: User,
            product: Product = None,
            balance: float = None,
            interest_rate: float = 0,
            instalment_rate: float | None = 0,
            constant_instalment: str = 'T',
            instalment_constant_value: float = 0,
            instalment_schedule: list = None,
            instalment_number: int = 12,
            start_date: datetime.date = None,
            decimal_places: int = 2
    ):
        self.user = user
        self.product = product
        self.balance = round(float(balance), 4) if balance is not None else None
        self.interest_rate = interest_rate or 0.0
        self.instalment_rate = float(instalment_rate or 0)
        self.constant_instalment = constant_instalment
        self.instalment_constant_value = float(instalment_constant_value or 0)
        self.instalment_schedule = instalment_schedule
        self.instalment_number = instalment_number or 12
        self.start_date = start_date
        self.decimal_places = decimal_places

        self._balance = self.balance
        self._balloon_interest_value: float = 0.0

        if not self.product:
            self.interest_required_total = 0.0

        else:
            state = self._get_state()
            assert state

            start_date = state['calc_date']
            self.instalment_schedule = self.product.schedule_set.filter(maturity_date__gte=start_date).order_by(
                'maturity_date')

            if not self.instalment_schedule:
                raise ValueError("Harmonogram spłat dla wybranego produktu jest już zakończony")

            self.start_date = state['calc_date']
            self.balance = round(float(state['balance']), self.decimal_places)
            self._balance = self.balance
            self.interest_required_total = round(float(state['interest_required_total']), self.decimal_places)

        if not self.balance:
            raise ValueError("balance must be set")

    def _calculate_instalment(
            self,
            instalment_constant_value: float,
            current_date,
            due_date,
            balloon):

        dt_int = self._get_date_interval(current_date, due_date)
        instalment_interest = self.calculate_instalment_interest(start_date=current_date, end_date=due_date)

        if balloon:
            return {
                INSTALMENT_MATURITY_DATE_SELECTOR: due_date,
                INSTALMENT_CAPITAL_SELECTOR: self._balance,
                INSTALMENT_COMMISSION_SELECTOR: 0.0,
                INSTALMENT_INTEREST_SELECTOR: instalment_interest + self._balloon_interest_value,
                INSTALMENT_TOTAL_SELECTOR: self._balance + instalment_interest,
                'balloon_interest_value': self._balloon_interest_value,
                'days': dt_int
            }

        if self.constant_instalment == 'T':
            self._balloon_interest_value = round(self._balloon_interest_value + instalment_interest,
                                                 self.decimal_places)

            instalment_capital = round(max(0.0, instalment_constant_value - instalment_interest), self.decimal_places)
            instalment_interest_underpaid = round(max(0, instalment_interest - instalment_constant_value),
                                                  self.decimal_places)
            instalment_interest = min(instalment_interest, instalment_constant_value)

            self._balloon_interest_value = round(self._balloon_interest_value - instalment_interest,
                                                 self.decimal_places)

        else:
            instalment_capital = round(self._balance * self.instalment_rate, self.decimal_places)
            instalment_interest_underpaid = 0.0

        return {
            INSTALMENT_MATURITY_DATE_SELECTOR: due_date,
            INSTALMENT_CAPITAL_SELECTOR: instalment_capital,
            INSTALMENT_COMMISSION_SELECTOR: 0.0,
            INSTALMENT_INTEREST_SELECTOR: instalment_interest,
            INSTALMENT_TOTAL_SELECTOR: instalment_capital + instalment_interest,
            'interest_underpaid': instalment_interest_underpaid,
            'balloon_interest_value': self._balloon_interest_value,
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
            end_date: datetime.date
    ):
        instalment_interest = 0

        days = self._get_date_interval(current_date=start_date, next_due_date=end_date)

        if not self.product or not self.product.in_default():
            return float(round(self._balance * self.interest_rate / 365 * days, self.decimal_places))

        for i in range(abs(start_date - end_date).days):
            interest_for_delay = ProductInterestGlobal.get_for(date=start_date + datetime.timedelta(days=i))
            instalment_interest += self._balance * float(interest_for_delay[0]) / 365

        return round(float(instalment_interest), self.decimal_places)

    def _calculate_due_date(self, due_date: datetime.date) -> datetime.date | None:
        if not due_date:
            return None

        weekday = due_date.weekday()
        delta = 7 - weekday if weekday > 4 else 0

        return due_date + datetime.timedelta(days=delta) if delta else due_date

    def _get_due_date(self, current_date: datetime.date) -> datetime.date | None:
        if not current_date:
            return None

        due_date = add_month(current_date, 1)
        return self._calculate_due_date(due_date)

    def _get_state(self, run_calculation=True):
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
            'interest_required_total': calculation.interest_per_day
        }

    def _get_instalment_schedule_maturity_date(self, instalment_schedule_item):
        if isinstance(instalment_schedule_item, ProductSchedule):
            return self._calculate_due_date(instalment_schedule_item.maturity_date)

        if type(instalment_schedule_item) == dict:
            return self._calculate_due_date(
                datetime.datetime.strptime(
                    instalment_schedule_item['maturityDate']['value'], settings.DATE_FORMAT).date() if
                instalment_schedule_item['maturityDate']['value'] else None
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

    def _get_maturity_date(self, schedule_date, current_date, recalculate_date):
        if self.instalment_schedule:
            if not recalculate_date:
                return self._get_instalment_schedule_maturity_date(schedule_date)

        return self._get_due_date(current_date)

    def calculate(self) -> dict:

        if not self.start_date:
            raise Exception("Do obliczenia harmonogramu wymagana jest data startu produktu")

        instalments = []
        instalment_capital_total = 0.0
        instalment_interest_total = 0.0
        instalment_value_total = 0.0

        current_date = self.start_date
        current_nominal_date = self.start_date

        recalculate_date = False

        for idx, i in enumerate(self.instalment_schedule[:self.instalment_number]) if self.instalment_schedule else enumerate(
                range(self.instalment_number)):

            if isinstance(i, dict) and 'change_flag' in i['maturityDate']:
                current_nominal_date = datetime.datetime.strptime(i['maturityDate']['value'], settings.DATE_FORMAT).date()
                recalculate_date = i['maturityDate']['change_flag'] == '2'

            due_date = self._get_maturity_date(i, current_nominal_date, recalculate_date)

            _instalment_constant_value = self.instalment_constant_value

            if self.instalment_schedule:
                _instalment_constant_value = round(float(self._get_instalment_schedule_total(i)['value']),
                                                   self.decimal_places) if self.constant_instalment else None

            instalment = self._calculate_instalment(
                instalment_constant_value=_instalment_constant_value,
                current_date=current_date,
                due_date=due_date,
                balloon=idx == len(self.instalment_schedule) - 1 \
                    if self.instalment_schedule \
                    else i == self.instalment_number - 1
            )

            if not idx:
                instalment[INSTALMENT_INTEREST_SELECTOR] += self.interest_required_total

            self._balance -= instalment[INSTALMENT_CAPITAL_SELECTOR]

            instalments.append(instalment)

            instalment_capital_total += instalment[INSTALMENT_CAPITAL_SELECTOR]
            instalment_interest_total += instalment[INSTALMENT_INTEREST_SELECTOR]
            instalment_value_total += instalment[INSTALMENT_TOTAL_SELECTOR]

            current_date = due_date

            current_nominal_date = add_month(current_nominal_date, 1)

        return {
            'sections': instalments,
            'aggregates': {
                INSTALMENT_CAPITAL_AGGREGATE: instalment_capital_total,
                INSTALMENT_INTEREST_AGGREGATE: instalment_interest_total,
                INSTALMENT_COMMISSION_AGGREGATE: 0,
                INSTALMENT_TOTAL_AGGREGATE: instalment_value_total
            }
        }
