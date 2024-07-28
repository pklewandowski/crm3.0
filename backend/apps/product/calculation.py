import abc
import collections
import datetime
import decimal

from django.db import transaction
from django.db.models import F, Sum, Max

from apps.document.models import DocumentTypeAccounting
from apps.product.models import ProductSchedule, ProductInterest, ProductCashFlow, Product, ProductCalculation
from apps.user.models import User


class CalculationDoesNotExist(Exception):
    pass


class CalculationException(Exception):
    pass


class CalculationBase:
    def __init__(self, product, user):
        self.user = user
        self.start_date = None
        self.end_date = None

        self.notifications = []

        if isinstance(product, Product):
            self.product = product
            self.id = product.id
        else:
            self.id = product
            self.product = Product.objects.get(pk=self.id)

        self.instalment_overdue_count = 0
        self.instalment_overdue_occurrence = 0
        self.instalment_daily = {}

        self.schedule_list = None
        self.schedule_list_keys = None
        self.schedule_current_date = None
        self.schedule_next_date = None
        self.schedule_date = None
        self.schedule_end_date = None
        self.schedule_maturity_due_date = None

        self.interest_list = None
        self.interest_code = None
        self.interest_rate = None

        self.interest_for_delay_rate = None
        self.interest_for_delay_rate_nominal = None
        self.interest_for_delay_rate_max = None
        self.interest_for_delay_rate_use = 'BOTH' if self.product.interest_for_delay_rate_use == 'XXX' else self.product.interest_for_delay_rate_use
        self.interest_for_delay_rate_use_current = 'MIN' if self.interest_for_delay_rate_use == 'BOTH' else self.interest_for_delay_rate_use
        """
        Interest for delay can be calculated not always basing on capital required (although mostly). There are some specific loans where
        the base for interest for delay calculation is greater than capital_required + nvl(commission_required, 0). the difference is constant.
        EXAMPLE. capital_gross = 200 000,00. There is ie. deposit = 100 000,00. So the interest_for_delay_calculation_add_value = 100 000,00 that means
        that total interest_for_delay_calculation_base = 300 000,00
        total product value = 200 000,00
        the difference is then 100 000,00
        self.interest_for_delay_calculation_base is changing the same way as capital_required (CAP_REQ)
        """
        self.interest_for_delay_calculation_add_value = self.product.interest_for_delay_calculation_add_value

        # current interest for delay calculation base = capital for interest calculation (1,2 or 3 version) + interest_for_delay_calculation_add_value
        self.interest_for_delay_calculation_base = decimal.Decimal(0)

        self.commission_list = None

        self.accounting_list = {}
        self.accounting_order = []
        self.accounting = {}

        self.days_in_year = 0

        self.delay_total = False

        self.notifications = None
        self.boot_user = User.objects.get(status='SYSTEM')
        self.rule_events = {}


class Calculation(CalculationBase):
    def __init__(self, product, user):
        super(Calculation, self).__init__(product, user)
        self.notifications = None
        self.boot_user = User.objects.get(status='SYSTEM')

        # initial settings
        self.set_end_date()
        self.set_schedule_list()
        self.set_interest_list()
        self.set_commission_list()
        self.set_accounting()
        self.set_initial_interest()
        self.set_schedule_end_date()

        if self.schedule_list:
            self.schedule_end_date = datetime.datetime.strptime(next(reversed(self.schedule_list)), '%Y-%m-%d').date()
        else:
            raise Exception('Calculation: No schedule list')

    def calculate_instalment_interest_required(self):
        return (self.accounting['CAP_NOT_REQ'] + self.accounting['CAP_REQ']) * self.interest_rate / 12

    def set_schedule_list(self):
        self.schedule_list = collections.OrderedDict({i['maturity_date'].strftime("%Y-%m-%d"):
            {
                'value': decimal.Decimal(i['value']),
                'instalment_capital': decimal.Decimal(i['instalment_capital']),
                'instalment_interest': decimal.Decimal(i['instalment_interest']),
                'instalment_commission': decimal.Decimal(i['instalment_commission'])
            } for i in ProductSchedule.objects.filter(
            product=self.product).values('maturity_date').annotate(
            value=Sum(F('instalment_capital') + F('instalment_interest') + F('instalment_commission')),
            instalment_capital=Sum(F('instalment_capital')),
            instalment_interest=Sum(F('instalment_interest')),
            instalment_commission=Sum(F('instalment_commission'))).order_by('maturity_date')
        })

        self.schedule_list_keys = list(self.schedule_list.keys())
        self.schedule_next_date = datetime.datetime.strptime(self.schedule_list_keys[0], '%Y-%m-%d').date() if self.schedule_list_keys[0] else None

        dt = self.product.start_date

        for k, v in self.schedule_list.items():
            days = max(1, (datetime.datetime.strptime(k, "%Y-%m-%d").date() - dt).days)
            self.instalment_daily[datetime.datetime.strftime(dt, "%Y-%m-%d")] = {
                'capital': v['instalment_capital'] / days,
                'commission': v['instalment_commission'] / days,
                'interest': v['instalment_interest'] / days
            }
            dt = datetime.datetime.strptime(k, "%Y-%m-%d").date()

    def set_interest_list(self):
        self.interest_list = {
            i.start_date.strftime("%Y-%m-%d"): {
                'statutory_rate': decimal.Decimal(i.statutory_rate),
                'delay_rate': decimal.Decimal(i.delay_rate),
                'delay_max_rate': decimal.Decimal(i.delay_max_rate),
                'code': i.type.code,
            } for i in ProductInterest.objects.filter(product=self.product).order_by('start_date')}

        # self.interest_for_delay_rate_nominal = self.interest_list[str(self.product.start_date)]['delay_rate']
        # self.interest_for_delay_rate_max = self.interest_list[str(self.product.start_date)]['delay_max_rate']

    def set_commission_list(self):
        self.commission_list = self.product.commission_set.all()

    def set_schedule_end_date(self):
        self.schedule_end_date = ProductSchedule.objects.filter(product=self.product).values('maturity_date').aggregate(Max('maturity_date'))['maturity_date__max']

    def set_end_date(self):
        self.end_date = min(self.product.end_date or datetime.date.today(), datetime.date.today())

    def set_accounting(self):
        for n in DocumentTypeAccounting.objects.filter(document_type=self.product.type).order_by('sq'):
            self.accounting[n.accounting_type.code] = decimal.Decimal(0)

            if n.accounting_type.is_accounting_order:
                self.accounting_order.append(n)

            if n.accounting_type.is_editable:
                self.accounting_list[n.accounting_type.code] = {
                    i['cash_flow_date'].strftime("%Y-%m-%d"): decimal.Decimal(i['value']) for i in
                    ProductCashFlow.objects.filter(
                        product=self.product,
                        type=n.accounting_type).exclude(cash_flow_date__isnull=True).values('cash_flow_date').annotate(
                        value=Sum('value')).order_by('cash_flow_date')
                }

    def set_initial_interest(self):
        pi = ProductInterest.objects.filter(product=self.product).order_by('start_date')[0]
        self.interest_code = pi.type.code
        self.interest_for_delay_rate = pi.delay_rate
        self.interest_for_delay_rate_max = pi.delay_max_rate
        self.interest_rate = pi.statutory_rate

    @transaction.atomic()
    def _save_calculation(self, calculation_list):
        ProductCalculation.objects.bulk_create(calculation_list)
        self.product.balance = calculation_list[-1].balance
        self.product.save()

    @transaction.atomic()
    def _save_actions(self, action_list):
        for i in action_list:
            i.save()

    @abc.abstractmethod
    def calculate(self, start_date=None, end_date=None, simulate=False):
        pass

    @abc.abstractmethod
    def calculate_statutory_interest(self, dt):
        pass

    @abc.abstractmethod
    def calculate_daily_interest_for_delay(self, dt):
        pass
