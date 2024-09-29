import copy
import datetime
import decimal
import logging

from django.db import transaction
from django.db.models import Max

from apps.product.calc_utils import calculate_interest_daily
from apps.product.calculation import Calculation, CalculationException
from apps.product.models import ProductCalculation, ProductAction, ProductActionDefinition, ProductStatusTrack, \
    ProductInterestGlobal
from apps.product.rules import Rules
from apps.product.utils.utils import ProductUtils
from apps.product.view.views import ProductActionManager

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class CalculateLoan(Calculation):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    def __init__(self, product, user):
        super().__init__(product, user)

        self.rules = Rules(calculation_object=self)

        self.interest_rate = self._get_interest_rate()

        # interest for delay value
        self.accounting['INTEREST_FOR_DELAY_VALUE'] = decimal.Decimal(0.0)

        # intrerest value
        self.accounting['INTEREST_VALUE'] = decimal.Decimal(0.0)
        self.accounting['INTEREST_REQUIRED'] = decimal.Decimal(0.0)

        # commission required and not required
        self.accounting['COMM_REQ'] = decimal.Decimal(0.0)
        self.accounting['COMM_NOT_REQ'] = self.product.commission

        # capital required and not required
        self.accounting['CAP_REQ'] = decimal.Decimal(0.0)

        # if tranche so load first tranche
        if self.tranche_list:
            self.accounting['CAP_NOT_REQ'] = list(self.tranche_list.items())[0][1]
        else:
            self.accounting['CAP_NOT_REQ'] = self.product.capital_net \
                if self.product.capital_type_calc_source == 'N' else self.product.value

        # payments
        self.accounting['PAYMENT'] = decimal.Decimal(0.0)

        # remissions
        self.accounting['REM_CAP'] = decimal.Decimal(0.0)
        self.accounting['REM_COMM'] = decimal.Decimal(0.0)
        self.accounting['REM_INTEREST_FOR_DELAY'] = decimal.Decimal(0.0)
        self.accounting['REM_INTEREST'] = decimal.Decimal(0.0)
        self.accounting['REM_COST'] = decimal.Decimal(0.0)

        # operational variables but defined as instance attributes to handle ProductCalculation inserts
        self._instalment_nominal = decimal.Decimal(0.0)
        self._cost_occurrence = decimal.Decimal(0.0)

        self._capital_required_from_schedule = decimal.Decimal(0.0)
        self._commission_required_from_schedule = decimal.Decimal(0.0)
        self._interest_required_from_schedule = decimal.Decimal(0.0)

        self._instalment_accounting_capital_required = decimal.Decimal(0.0)
        self._instalment_accounting_capital_not_required = decimal.Decimal(0.0)
        self._instalment_accounting_commission_required = decimal.Decimal(0.0)
        self._instalment_accounting_commission_not_required = decimal.Decimal(0.0)
        self._instalment_accounting_interest_required = decimal.Decimal(0.0)
        self._instalment_accounting_interest_for_delay = decimal.Decimal(0.0)
        self._instalment_accounting_cost = decimal.Decimal(0.0)

        self._instalment_payment_overdue = False

        self._cost_total = decimal.Decimal(0.0)

        self._interest_for_delay_total = decimal.Decimal(0.0)
        self._instalment_total = decimal.Decimal(0.0)

        self._capital_daily = decimal.Decimal(0.0)
        self._commission_daily = decimal.Decimal(0.0)
        self._interest_daily = decimal.Decimal(0.0)

        self._capital_per_day = decimal.Decimal(0.0)
        self._commission_per_day = decimal.Decimal(0.0)
        self._interest_per_day = decimal.Decimal(0.0)
        self._interest_cumulated_per_day = decimal.Decimal(0.0)

        self._calculation_list = []
        self._action_list = []

        self._interest_for_delay_daily = decimal.Decimal(0.0)

        # _undo_interest_for_delay flag indicating if instalment was paid before grace_period and then need to undo interest for delay
        # for <current_schedule_date; payment_day> range
        # interest for delay undo is set as correction in today value
        self._undo_interest_for_delay = False
        self._current_payment = decimal.Decimal(0.0)

        self._remission_capital = decimal.Decimal(0.0)
        self._remission_commission = decimal.Decimal(0.0)
        self._remission_interest = decimal.Decimal(0.0)
        self._remission_interest_for_delay = decimal.Decimal(0.0)
        self._remission_cost = decimal.Decimal(0.0)

        self.schedule_current_date_str = list(self.schedule_list.keys())[0]
        self.schedule_current_date = datetime.datetime.strptime(self.schedule_current_date_str, '%Y-%m-%d').date()

        self._delay = False

        self._calculation_list = []
        self._action_list = []

        self._payment_in_grace_period = False

    def __enter__(self):
        self.recount_required_date_creation_marker = self.product.recount_required_date_creation_marker
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.recount_required_date_creation_marker == self.product.recount_required_date_creation_marker:
            self.product.recount_required_date_creation_marker = None
            self.product.recount_required_date = None
            self.product.save()

    def _get_interest_rate(self):
        return self.product.instalment_interest_rate

    def calculate_statutory_interest(self, dt):
        return decimal.Decimal(self.product.capital_net * self.interest_rate / self.days_in_year)

    def calculate_daily_interest_for_delay(self, dt):
        due_date = self.schedule_current_date

        commission = self.accounting['COMM_NOT_REQ'] + self.accounting['COMM_REQ']
        capital = self.accounting['CAP_NOT_REQ'] + self.accounting['CAP_REQ']

        self._delay = False

        self.interest_for_delay_calculation_base = decimal.Decimal(0)

        if self._instalment_payment_overdue:
            self._delay = True and not self._undo_interest_for_delay

            if dt >= due_date + datetime.timedelta(days=self.product.grace_period):
                self.delay_total = self.delay_total or not self._undo_interest_for_delay

        if self._undo_interest_for_delay:
            return decimal.Decimal(0.0)

        daily_interest = 0.0

        if self.interest_code == '1' \
                and self._delay \
                and (self.accounting['INTEREST_FOR_DELAY_VALUE'] != 0 or
                     ((self.accounting['COMM_REQ'] > 0 or self.accounting[
                         'CAP_REQ'] > 0) and due_date is not None and dt >= due_date)):

            self.interest_for_delay_calculation_base = self.accounting['COMM_REQ'] + self.accounting[
                'CAP_REQ'] + self.interest_for_delay_calculation_add_value
            daily_interest = (
                                     self.interest_for_delay_calculation_base * self.interest_for_delay_rate) / self.days_in_year

        elif self.interest_code == '2' \
                and self._delay \
                and (self.accounting['INTEREST_FOR_DELAY_VALUE'] != 0 or
                     ((self.accounting['COMM_REQ'] > 0 or self.accounting[
                         'CAP_REQ'] > 0) and due_date is not None and dt >= due_date)):

            self.interest_for_delay_calculation_base = commission + capital + self.interest_for_delay_calculation_add_value
            daily_interest = self.interest_for_delay_calculation_base * self.interest_for_delay_rate / self.days_in_year

        elif self.interest_code == '3' and (self._delay or self.delay_total) and (
                # jeśli są już odsetki naliczone lub jest co najmniej grace_period dni po dacie wymagalności
                # jeśli są odsetki to nie czekamy jednego dnia z ich naliczeniem, tylko od razu naliczamy
                self.accounting['INTEREST_FOR_DELAY_VALUE'] != 0 or (due_date is not None and dt >= due_date)
        ):
            self.interest_for_delay_calculation_base = commission + capital + self.interest_for_delay_calculation_add_value
            daily_interest = (
                                     self.interest_for_delay_calculation_base * self.interest_for_delay_rate) / self.days_in_year

        return decimal.Decimal(daily_interest)

    def _register_action(self, action_code, dt, calc, action_list):
        action = ProductActionDefinition.objects.get(pk=action_code)

        try:
            ProductAction.objects.get(product=self.product, action=action, action_execution_date=dt)
        except ProductAction.DoesNotExist:

            pam = ProductActionManager(
                id_product=self.product.pk,
                id_action=action_code,
                user=self.boot_user
            )

            ds = pam.get_datasource(product_calculation=calc)

            action_list.append(
                ProductAction(
                    product=self.product,
                    action=action,
                    name=action.name,
                    action_date=datetime.datetime.now(),
                    created_by=self.boot_user,
                    datasource=ds,
                    action_execution_date=dt
                )
            )

    def __handle_remissions(self, dt_str):
        self._remission_capital = decimal.Decimal(0.0)
        self._remission_commission = decimal.Decimal(0.0)
        self._remission_interest = decimal.Decimal(0.0)
        self._remission_interest_for_delay = decimal.Decimal(0.0)
        self._remission_cost = decimal.Decimal(0.0)
        # ----------------------------- Handling remissions --------------------------------------
        # remission of capital
        if dt_str in self.accounting_list['REM_CAP']:
            val_d = self.accounting_list['REM_CAP'][dt_str]

            # ustalenie maksymalnej możliwej kwoty na rozksięgowanie dla danego typu
            # zaokrąglenie, żeby poprawne były obliczenia (nie uciekał 1 grosz)
            val = round(min(self.accounting['CAP_REQ'], val_d), 3)
            self.accounting['CAP_REQ'] -= val
            self._remission_capital += val

            val = round(min(self.accounting['CAP_NOT_REQ'], val_d - val), 3)
            self.accounting['CAP_NOT_REQ'] -= val
            self._remission_capital += val

        # remission of commission
        if dt_str in self.accounting_list['REM_COMM']:
            val_d = self.accounting_list['REM_COMM'][dt_str]

            val = round(min(self.accounting['COMM_REQ'], val_d), 3)
            self.accounting['COMM_REQ'] -= val
            self._remission_commission += val

            val = round(min(self.accounting['COMM_NOT_REQ'], val_d - val), 3)
            self.accounting['COMM_NOT_REQ'] -= val
            self._remission_commission += val

        # remission of interest
        if dt_str in self.accounting_list['REM_INTEREST']:
            val_d = self.accounting_list['REM_INTEREST'][dt_str]
            val = round(min(self.accounting['INTEREST_VALUE'], val_d), 3)
            self.accounting['INTEREST_VALUE'] -= val
            self._remission_interest = val

        # remission of interest for delay
        if dt_str in self.accounting_list['REM_INTEREST_FOR_DELAY']:
            val_d = self.accounting_list['REM_INTEREST_FOR_DELAY'][dt_str]
            val = round(min(self.accounting['INTEREST_FOR_DELAY_VALUE'], val_d), 3)
            self.accounting['INTEREST_FOR_DELAY_VALUE'] -= val
            self._remission_interest_for_delay = val

        # remission of cost
        if dt_str in self.accounting_list['REM_COST']:
            val_d = self.accounting_list['REM_COST'][dt_str]
            val = round(min(self.accounting['COST'], val_d), 3)
            self.accounting['COST'] -= val
            self._remission_cost = val

    def book_payment_with_accounting_order(self, dt_str: str, ignore_due_day=False):
        if dt_str == self.schedule_current_date_str \
                and self.schedule_list[self.schedule_current_date_str]['instalment_total'] > self.accounting['PAYMENT']:
            self._instalment_payment_overdue = True and not self._undo_interest_for_delay

        if self.accounting['PAYMENT'] == 0:
            # there is nothing to account
            return

        for i in self.accounting_order:
            # book only on due date
            if dt_str not in self.schedule_list and not ignore_due_day:
                if i.accounting_type.due_day_accounting_only:
                    continue

            # ustalenie maksymalnej możliwej kwoty na rozksięgowanie dla danego typu
            # zaokrąglenie, żeby poprawne były obliczenia (nie uciekał 1 grosz)
            val = round(min(self.accounting[i.accounting_type.code], self.accounting['PAYMENT']), 3)

            # pomniejszenie wpłaty o wartość dla danego typu zobowiązania
            self.accounting['PAYMENT'] = self.accounting['PAYMENT'] - val

            # odjęcie od wartości danego księgowania możliwej wartości kwoty z wpłaty (val)
            if i.accounting_type.min_value is not None:
                self.accounting[i.accounting_type.code] = max(i.accounting_type.min_value,
                                                              self.accounting[i.accounting_type.code] - val)
            else:
                self.accounting[i.accounting_type.code] = self.accounting[i.accounting_type.code] - val

            # rozbicie raty na składowe dla danych typów księgowań
            if i.accounting_type.code == 'INTEREST_FOR_DELAY_VALUE':
                self._instalment_accounting_interest_for_delay = val

            elif i.accounting_type.code == 'COST':
                self._instalment_accounting_cost = val

            elif i.accounting_type.code == 'CAP_REQ':
                self._instalment_accounting_capital_required = val
                self._capital_per_day = max(0, self._capital_per_day - val)

            elif i.accounting_type.code == 'CAP_NOT_REQ':
                self._instalment_accounting_capital_not_required = val

            elif i.accounting_type.code == 'COMM_REQ':
                self._instalment_accounting_commission_required = val
                self._commission_per_day = max(0, self._commission_per_day - val)

            elif i.accounting_type.code == 'COMM_NOT_REQ':
                self._instalment_accounting_commission_not_required = val

            elif i.accounting_type.code == 'INTEREST_REQUIRED':
                self._instalment_accounting_interest_required = val
                self._interest_per_day = max(0, self._interest_per_day - val)

    def capitalize(self):
        self.accounting['CAP_REQ'] += self.accounting['CAP_NOT_REQ']  # + self.accounting['INTEREST_FOR_DELAY_VALUE']
        self.accounting['CAP_NOT_REQ'] = decimal.Decimal(0)
        # self.accounting['INTEREST_FOR_DELAY_VALUE'] = decimal.Decimal(0.0)

        self.interest_for_delay_rate_use_current = 'MAX'

    def terminate(self):
        return

    def fill_calculation_table(self, dt):
        self._calculation_list.append(
            ProductCalculation(
                id=datetime.date.strftime(dt, '%Y%m%d') + str(self.product.pk),
                product=self.product,
                product_status=self.product.status,
                calc_date=dt,

                balance=ProductUtils.calculate_balance(
                    {
                        'capital_not_required': self.accounting['CAP_NOT_REQ'],
                        'commission_not_required': self.accounting['COMM_NOT_REQ'],
                        'interest_for_delay_required': self.accounting['INTEREST_FOR_DELAY_VALUE'],
                        'required_liabilities_sum': (
                                self.accounting['CAP_REQ'] +
                                self.accounting['COMM_REQ'] +
                                self._interest_per_day
                        ),
                        'cost': self.accounting['COST'],
                        'instalment_overpaid': self.accounting['PAYMENT']
                    }
                ),
                capital_per_day=self._capital_per_day,
                capital_required=self.accounting['CAP_REQ'],
                capital_not_required=self.accounting['CAP_NOT_REQ'],
                capital_required_from_schedule=self._capital_required_from_schedule,

                commission_per_day=self._commission_per_day,
                commission_required_from_schedule=self._commission_required_from_schedule,
                commission_required=self.accounting['COMM_REQ'],
                commission_not_required=self.accounting['COMM_NOT_REQ'],

                interest_daily=self._interest_daily,
                interest_per_day=self._interest_per_day,
                interest_cumulated_per_day=self._interest_cumulated_per_day,
                interest_required=self._interest_per_day,  # self.accounting['INTEREST_REQUIRED'],
                interest_required_from_schedule=self._interest_required_from_schedule,
                interest_rate=self.interest_rate * 100,

                interest_for_delay_calculation_base=self.interest_for_delay_calculation_base,
                interest_for_delay_total=self._interest_for_delay_total,
                interest_for_delay_required=self.accounting['INTEREST_FOR_DELAY_VALUE'],
                interest_for_delay_required_daily=self._interest_for_delay_daily,
                interest_for_delay_rate=self.interest_for_delay_rate * 100,

                required_liabilities_sum=self.accounting['CAP_REQ'] +
                                         self.accounting['COMM_REQ'] +
                                         self.accounting['INTEREST_REQUIRED'],

                required_liabilities_sum_from_schedule=(self._capital_required_from_schedule +
                                                        self._commission_required_from_schedule +
                                                        self._interest_required_from_schedule),

                cost=self.accounting['COST'],
                cost_occurrence=self._cost_occurrence,
                cost_total=self._cost_total,

                instalment=self._instalment_nominal,
                instalment_total=self._instalment_total,
                instalment_overpaid=self.accounting['PAYMENT'],

                instalment_accounting_capital_required=self._instalment_accounting_capital_required,
                instalment_accounting_capital_not_required=self._instalment_accounting_capital_not_required,
                instalment_accounting_commission_required=self._instalment_accounting_commission_required,
                instalment_accounting_commission_not_required=self._instalment_accounting_commission_not_required,
                instalment_accounting_interest_required=self._instalment_accounting_interest_required,
                instalment_accounting_interest_for_delay=self._instalment_accounting_interest_for_delay,
                instalment_accounting_cost=self._instalment_accounting_cost,

                instalment_overdue_count=self.instalment_overdue_count,
                instalment_overdue_occurrence=self.instalment_overdue_occurrence,

                remission_capital=self._remission_capital,
                remission_commission=self._remission_commission,
                remission_interest=self._remission_interest,
                remission_interest_for_delay=self._remission_interest_for_delay,
                remission_cost=self._remission_cost
            )
        )

    def update_operational_variables(self, dt, dt_str):

        # reset operational variables for new loop pass
        self._instalment_nominal = decimal.Decimal(0.0)
        self._cost_occurrence = decimal.Decimal(0.0)

        self._capital_required_from_schedule = decimal.Decimal(0.0)
        self._commission_required_from_schedule = decimal.Decimal(0.0)
        self._interest_required_from_schedule = decimal.Decimal(0.0)

        self._instalment_accounting_capital_required = decimal.Decimal(0.0)
        self._instalment_accounting_capital_not_required = decimal.Decimal(0.0)

        self._instalment_accounting_commission_required = decimal.Decimal(0.0)
        self._instalment_accounting_commission_not_required = decimal.Decimal(0.0)

        self._instalment_accounting_interest_required = decimal.Decimal(0.0)
        self._instalment_accounting_interest_for_delay = decimal.Decimal(0.0)

        self._instalment_accounting_cost = decimal.Decimal(0.0)

        # calculate instalment daily values
        if dt_str in self.instalment_daily:
            self._capital_daily = self.instalment_daily[dt_str]['capital']
            self._commission_daily = self.instalment_daily[dt_str]['commission']

        # calculate daily interest for delay
        self.interest_for_delay_rate_nominal, self.interest_for_delay_rate_max = ProductInterestGlobal.get_for(dt)

        # if dt_str in self.interest_list:
        #     # set interest for delay type (nominal or max) depending on product current status
        #     self.interest_for_delay_rate_nominal = self.interest_list[dt_str]['delay_rate']
        #     self.interest_for_delay_rate_max = self.interest_list[dt_str]['delay_max_rate']
        #
        #     self.interest_rate = self.interest_list[dt_str]['statutory_rate']
        #     self.interest_code = self.interest_list[dt_str]['code']

        self.interest_for_delay_rate = self.interest_for_delay_rate_nominal \
            if self.interest_for_delay_rate_use_current == 'MIN' else self.interest_for_delay_rate_max

        self._interest_for_delay_daily = self.calculate_daily_interest_for_delay(dt)

        self.accounting['INTEREST_FOR_DELAY_VALUE'] += self._interest_for_delay_daily
        self._interest_for_delay_total += self._interest_for_delay_daily

        self._interest_daily = calculate_interest_daily(
            capital_total=self.accounting['CAP_REQ'] + self.accounting['CAP_NOT_REQ'],
            interest_rate=self.interest_rate,
            days_in_year=self.days_in_year
        ) if not self._delay and dt > self.product.start_date else decimal.Decimal(0)

        # update per-day values of capital, commission and interest
        self._capital_per_day += self._capital_daily
        self._commission_per_day += self._commission_daily
        self._interest_per_day += self._interest_daily
        self._interest_cumulated_per_day += self._interest_daily
        self.accounting['INTEREST_VALUE'] += self._interest_daily

    def update_state(self, dt, dt_str):
        """
        Updates values from schedule entry
        :param dt:
        :param dt_str:
        :return:
        """

        # if there is a tranche to be added, add it to the capital not required
        if (
                self.tranche_list
                and dt_str != datetime.datetime.strftime(self.product.start_date, '%Y-%m-%d')
                and dt_str in self.tranche_list
        ):
            self.accounting['CAP_NOT_REQ'] += self.tranche_list[dt_str]

        # if there is payment on the list
        if dt_str in self.accounting_list['PAYMENT']:
            val = self.accounting_list['PAYMENT'][dt_str]
            self._instalment_nominal = val
            self._instalment_total += val
            self.accounting['PAYMENT'] += val

            # todo: jeśli zobowiązania nie do końca zapłacone, to nie odejmuje!
            # todo: wyjaśnić, czy niespłacona jak wartość raty niespłacona, czy jak wszystkie zobowiązania niespłacone!!!
            self.instalment_overdue_count -= 1

            # TODO: Jeśli kapitał wpłat, czyli self.accounting['PAYMENT'] jest niższy niż wymagalny, to informacja do pracownika

        # if maturity day has come (instalment payment day)
        if dt_str in self.schedule_list:
            val = self.schedule_list[dt_str]

            # set the current and next maturity date for handle rules
            self.schedule_current_date_str = dt_str
            self.schedule_current_date = datetime.datetime.strptime(dt_str, '%Y-%m-%d').date()

            try:
                self.schedule_next_date = datetime.datetime.strptime(
                    self.schedule_list_keys[self.schedule_list_keys.index(dt_str) + 1], '%Y-%m-%d').date()
            except IndexError:
                self.schedule_next_date = None

            # TODO: TYLKO do testów - to jest DRUT dla raty stałej
            cap_req = max(0, val['instalment_total'] - self._commission_per_day - self._interest_per_day)
            self._capital_required_from_schedule = min(cap_req, self.accounting['CAP_NOT_REQ'])
            self._commission_required_from_schedule = min(self._commission_per_day, self.accounting['COMM_NOT_REQ'])
            self._interest_required_from_schedule = self._interest_per_day

            self.accounting['INTEREST_REQUIRED'] = self._interest_per_day

            # Swich-ujemy kapitał /prow niewymagalny (czyli przerzucamy na kapitał/prow wymagalny z kapitału niewymagalnego: (CAP_REQ += val), (CAP_NOT_REQ -= val))
            oper = min(self.accounting['COMM_NOT_REQ'], self._commission_required_from_schedule)
            self.accounting['COMM_REQ'] += oper
            self.accounting['COMM_NOT_REQ'] -= oper

            oper = min(self.accounting['CAP_NOT_REQ'], self._capital_required_from_schedule)
            self.accounting['CAP_REQ'] += oper
            self.accounting['CAP_NOT_REQ'] -= oper
            #

            # Sprawdzenie zaległości we wpłatach rat. Add overdues to eventually diminish it in accounting
            self.instalment_overdue_count += 1
            self.instalment_overdue_occurrence += 1

        # if constant instalment, then calculate CAP_REQ <-> INTEREST_REQUIRED balance

        if self.accounting['CAP_REQ'] and dt > self.schedule_current_date:
            oper = min(self.accounting['CAP_REQ'], self._interest_daily)
            self.accounting['CAP_REQ'] -= oper
            self.accounting['CAP_NOT_REQ'] += oper

            if self.accounting['INTEREST_REQUIRED']:
                self.accounting['INTEREST_REQUIRED'] += self._interest_daily


        if dt_str in self.accounting_list['COST']:
            val = self.accounting_list['COST'][dt_str]
            self._cost_occurrence = val
            self._cost_total += val
            self.accounting['COST'] += val

        self.__handle_remissions(dt_str)

    def save(self, simulation=False):
        if not simulation:
            # delete all calculation rows where calc_date >= start_date to load recounted rows
            ProductCalculation.objects.filter(product=self.product, calc_date__gte=self.start_date).delete()

            if self._calculation_list:
                self._save_calculation(self._calculation_list)
            self._save_actions(self._action_list)

    def _get_max_calculation_data(self, dt):
        """
        :param dt: nominal given calculation start date passed as parameter to calculate() def or product.start_date if empty
        :return: {max_date: date, calc:calculation_data}.
        max_date calculation is valid minus 1 day, so
        """

        if dt is None:
            raise ValueError(
                '[%s][set_calculation_starting_state]: dt date must be specified' % self.__class__.__name__)

        if dt == self.product.start_date:
            return {'max_date': dt, 'calc': None}

        try:
            calc = ProductCalculation.objects.get(product=self.product, calc_date=dt - datetime.timedelta(days=1))
            return {'max_date': dt, 'calc': calc}

        except ProductCalculation.DoesNotExist:
            max_date = ProductCalculation.objects.filter(product=self.product).aggregate(Max('calc_date'))[
                'calc_date__max']
            if max_date:
                return {'max_date': max_date,
                        'calc': ProductCalculation.objects.get(product=self.product, calc_date=max_date)}
            else:
                return {'max_date': self.product.start_date, 'calc': None}

    def __revert_product_state(self, dt):
        ProductStatusTrack.objects.filter(product=self.product,
                                          effective_date__gte=dt,
                                          is_initial=False
                                          ).delete()
        self.product.status = self.product.status_track_set.all().order_by('-effective_date')[0].status
        self.product.save()

    def _set_calculation_state(self, calc):
        if calc:
            self.accounting['CAP_REQ'] = calc.capital_required
            self.accounting['CAP_NOT_REQ'] = calc.capital_not_required
            self._capital_required_from_schedule = calc.capital_required_from_schedule

            self.accounting['COMM_REQ'] = calc.commission_required
            self.accounting['COMM_NOT_REQ'] = calc.commission_not_required
            self._commission_per_day = calc.commission_per_day
            self._commission_required_from_schedule = calc.commission_required_from_schedule

            self._interest_per_day = calc.interest_per_day
            self._interest_cumulated_per_day = calc.interest_cumulated_per_day
            self._interest_required_from_schedule = calc.interest_required_from_schedule
            self.interest_rate = round(calc.interest_rate / 100, 4)

            self.accounting['INTEREST_VALUE'] = calc.interest_per_day
            self.accounting['INTEREST_REQUIRED'] = calc.interest_required

            self._interest_for_delay_total = calc.interest_for_delay_total

            self.accounting['INTEREST_FOR_DELAY_VALUE'] = calc.interest_for_delay_required
            self._interest_for_delay_daily = calc.interest_for_delay_required_daily
            self.interest_for_delay_rate = round(calc.interest_for_delay_rate / 100, 4)

            self.accounting['COST'] = calc.cost
            self._cost_occurrence = calc.cost_occurrence
            self._cost_total = calc.cost_total

            self._instalment_nominal = calc.instalment
            self._instalment_total = calc.instalment_total
            self.accounting['PAYMENT'] = calc.instalment_overpaid

            self._instalment_accounting_capital_required = calc.instalment_accounting_capital_required
            self._instalment_accounting_capital_not_required = calc.instalment_accounting_capital_not_required
            self._instalment_accounting_commission_required = calc.instalment_accounting_commission_required
            self._instalment_accounting_commission_not_required = calc.instalment_accounting_commission_not_required
            self._instalment_accounting_interest_required = calc.instalment_accounting_interest_required
            self._instalment_accounting_interest_for_delay = calc.instalment_accounting_interest_for_delay
            self._instalment_accounting_cost = calc.instalment_accounting_cost

            self.instalment_overdue_count = calc.instalment_overdue_count
            self.instalment_overdue_occurrence = calc.instalment_overdue_occurrence

            self._remission_capital = calc.remission_capital
            self._remission_commission = calc.remission_commission
            self._remission_interest = calc.remission_interest
            self._remission_interest_for_delay = calc.remission_interest_for_delay
            self._remission_cost = calc.remission_cost

    def set_calculation_initial_state(self, dt):
        if dt is None:
            raise ValueError(
                '[%s][set_calculation_starting_state]: `dt` parameter must not be none' % self.__class__.__name__)

        max_calc_data = self._get_max_calculation_data(dt)

        if max_calc_data is None:
            raise CalculationException(
                '[%s][set_calculation_starting_state]: wartość `max_calc_data` nie może być pusta' % self.__class__.__name__)

        max_date, calc = max_calc_data.values()

        if not max_date:
            raise CalculationException(
                '[%s][set_calculation_starting_state]: parametr `max_date` nie może być pusty' % self.__class__.__name__)

        # reverting document state to that which was in max_date - 1 -> day before calculation starts
        self.__revert_product_state(max_date)

        filter_schedule_list = filter(lambda x: x < max_date, list(
            map(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').date(), self.schedule_list)))

        try:
            self.schedule_current_date = max(list(filter_schedule_list))
            self.schedule_current_date_str = datetime.datetime.strftime(self.schedule_current_date, '%Y-%m-%d')

        except ValueError:
            # schedule_current_date should stay as initial
            pass

        self._set_calculation_state(calc)

        return max_date

    """
    start_date should be min date of all updates made by user (in schedule, interest and cash_flow data)
    """

    def _get_calculation_entry(self, dt):
        for idx, i in enumerate(self._calculation_list):
            if i.calc_date == dt:
                return {"idx": idx, "entry": i}
        return None

    def _get_grace_period_payment(self, dt):
        calculation_due_day = self._get_calculation_entry(self.schedule_current_date)
        if not calculation_due_day:
            raise Exception('calc.recount_grace_period: no calculation_due_day')

        calculation_dt = self._get_calculation_entry(dt)
        if not calculation_dt:
            raise Exception('calc.recount_grace_period: no calculation_dt')

        start_calculation = self._calculation_list[max(0, calculation_due_day['idx'] - 1)]

        # get sum of payments during grace period. As a start value get possible instalment_overpaid value for starting day
        payment = start_calculation.instalment_overpaid

        for idx in range(calculation_due_day['idx'], calculation_dt['idx'] + 1):
            payment += self._calculation_list[idx].instalment

        instalment_required = self.schedule_list[self.schedule_current_date_str]['instalment_total']

        return {'payment': payment, 'result': payment >= instalment_required,
                'calculation_due_day': calculation_due_day}

    def _undo_instalment_overdue(self, dt, payment_value):
        start, end = (
            self._get_calculation_entry(self.schedule_current_date),
            self._get_calculation_entry(dt)
        )

        total_instalment = (
                start['entry'].capital_required_from_schedule + start['entry'].interest_required_from_schedule
        )

        capital_total = start['entry'].capital_required + start['entry'].capital_not_required - total_instalment

        interest_daily = calculate_interest_daily(
            capital_total=capital_total,
            interest_rate=start['entry'].interest_rate / 100,
            days_in_year=self.days_in_year
        )

        interest_cumulated_per_day = start['entry'].interest_cumulated_per_day

        for e_idx, idx in enumerate(range(start['idx'], end['idx'] + 1)):
            start_entry = copy.copy(start['entry'])
            start_entry.id = self._calculation_list[idx].id
            self._calculation_list[idx] = start_entry

            # re-set interest for delay values
            self._calculation_list[idx].interest_for_delay_required = decimal.Decimal(0)
            self._calculation_list[idx].interest_for_delay_required_daily = decimal.Decimal(0)
            self._calculation_list[idx].interest_for_delay_total = start['entry'].interest_for_delay_total
            self._calculation_list[idx].interest_for_delay_calculation_base = decimal.Decimal(0)

            # re-set interest values
            self._calculation_list[idx].interest_required = start['entry'].interest_required
            self._calculation_list[idx].interest_daily = interest_daily
            self._calculation_list[idx].interest_per_day = interest_daily * e_idx
            self._calculation_list[idx].interest_cumulated_per_day = interest_cumulated_per_day + interest_daily * e_idx

        # accounting
        # self._calculation_list[end['idx']].pay
        self.book_payment_with_accounting_order(
            dt_str=datetime.datetime.strftime(self._calculation_list[end['idx']].calc_date, '%Y-%m-%d'),
            ignore_due_day=True
        )

        # --
        # update operational variables
        self._interest_per_day = self._calculation_list[end['idx']].interest_per_day
        self._interest_for_delay_daily = decimal.Decimal(0)
        self._interest_for_delay_total = start['entry'].interest_for_delay_total
        self._delay = False

        self.accounting['INTEREST_FOR_DELAY_VALUE'] = decimal.Decimal(0)

    def calculate(self, start_date=None, end_date=None, simulation=False):
        logger.debug('Calculation started')

        with transaction.atomic():
            # ---------------------------------- INIT ------------------------------------------
            # getting nominal start date
            dt = start_date if start_date else self.product.start_date

            if dt < self.product.start_date:
                raise CalculationException(
                    f'Kalkulacja produktu {self.product.document.code} ({str(self.product.document.owner)}) '
                    f'będzie możliwa dopiero po osiągnięciu daty startu: {self.product.start_date}')

            # get the real possible start date of the calculation and set the calculation initial state
            # for one day before start_date
            dt = self.set_calculation_initial_state(dt)

            if dt is None:
                dt = self.product.start_date
            if dt > datetime.date.today():
                return

            self.start_date, self.end_date = dt, min(end_date or datetime.date.today(),
                                                     datetime.date.today(),
                                                     self.product.end_date or datetime.date.today())

            # const days in year regardless of year days count if CONSTANT_DAYS_IN_YEAR == True
            self.days_in_year = 365  # if CONSTANT_DAYS_IN_YEAR == True else py3ws_utils.days_in_year(dt.year)

            # --------------------------------- MAIN LOOP -------------------------------------
            while dt < self.end_date:
                # set days in year if new year incoming
                # if dt.month == 1 and dt.day == 1:
                # self.days_in_year = 365  # py3ws_utils.days_in_year(dt.year)

                dt_str = dt.strftime('%Y-%m-%d')

                # capitalization
                if dt == self.product.capitalization_date:
                    self.capitalize()
                    self.rule_events['AGR_CAPITALIZATION'] = {'due_date': dt}

                # update operational variables for the current loop pass. Some reset to 0, some aggregate etc.
                self.update_operational_variables(dt, dt_str)

                # set values state for a day
                self.update_state(dt, dt_str)

                # book payment following the accounting order on maturity day incoming
                self.book_payment_with_accounting_order(dt_str=dt_str, ignore_due_day=self._undo_interest_for_delay)

                # termination
                if dt == self.product.termination_date:
                    self.terminate()
                    self.rule_events['AGR_TERMINATION'] = {'due_date': dt}

                # agreement end
                if dt == self.schedule_end_date:
                    self.rule_events['AGR_END'] = {'due_date': dt}

                # handle financial rules for the document
                self.rules.handle_rules(dt, data={
                    'SCHEDULE_CURRENT_DATE': self.schedule_current_date,
                    'SCHEDULE_NEXT_DATE': self.schedule_next_date,
                    'INSTALMENT_OVERDUE_OCCURRENCE': self.instalment_overdue_occurrence,
                    'INSTALMENT_OVERDUE_COUNT': self.instalment_overdue_count,
                    'RULE_EVENTS': self.rule_events
                })

                # fill calculation table
                self.fill_calculation_table(dt)

                # set undo_interest_for_delay to false if grace_period reached and instalment fully paid
                if dt > self.schedule_current_date:
                    if (dt - self.schedule_current_date).days < self.product.grace_period:
                        if not self.delay_total and not self._undo_interest_for_delay:
                            recount = self._get_grace_period_payment(dt)

                            if recount['result']:
                                # self._instalment_payment_overdue = False
                                # self._undo_instalment_overdue(dt, recount['payment'])

                                self._calculation_list = self._calculation_list[:recount['calculation_due_day']['idx']] \
                                    if recount['calculation_due_day']['idx'] > 0 else [self._calculation_list[0]]

                                dt = self._calculation_list[-1].calc_date

                                self._set_calculation_state(self._calculation_list[-1])

                                self._undo_interest_for_delay = True
                                self._instalment_payment_overdue = False

                    else:
                        self._undo_interest_for_delay = False

                dt += datetime.timedelta(days=1)

            self.save(simulation=simulation)

        return self._calculation_list
