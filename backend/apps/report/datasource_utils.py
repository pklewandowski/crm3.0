import datetime

from apps.document.models import Document
from apps.product.models import ProductCalculation
from apps.user.models import User


class ReportDatasourceUtils:
    document = None
    user = None
    product_calculation = None

    def _get_product_calculation(self):
        if not self.document.product:
            self.product_calculation = None
            return
        if not self.product_calculation:
            self.product_calculation = ProductCalculation.objects.get(product=self.document.product, calc_date=datetime.date.today())

    def __init__(self, *args, **kwargs):
        self.document = kwargs.pop('document', None)
        self.user = kwargs.pop('user', None)
        self.product_calculation = kwargs.pop('product_calculation', None)

        if not self.user:
            raise Exception('Obiekt użytkownika nie może być pusty')

        if not self.document:
            raise Exception('Próba wybrania dokumentu zakończona niepowodzeniem')

    def get_creation_date(self):
        return "{:%Y-%m-%d}".format(datetime.date.today())

    def get_logged_user(self):
        if self.user:
            return "%s %s" % (self.user.first_name, self.user.last_name)
        else:
            return None

    def get_creditor(self):
        return "Speed Cash Polska Sp. z o. o."

    def get_creditor_address(self):
        return "Mazowiecka 9<br/>00-052 Warszawa"

    def get_creditor_bank_account(self):
        return '77 6666 5555 4444 3333 2222 1111'

    def get_agreement_no(self):
        return self.document.code

    def get_loan_start_date(self):
        if self.document.product.start_date:
            return "{:%Y-%m-%d}".format(self.document.product.start_date)
        else:
            return ''

    def get_loan_schedule_end_date(self):
        if self.document.product.end_date:
            return "{:%Y-%m-%d}".format(self.document.product.end_date)
        else:
            return ''

    def get_capital_required(self):
        self._get_product_calculation()
        if self.product_calculation:
            return '{0:.2f}'.format(self.product_calculation.capital_required)
        else:
            return ''

    def get_capital_not_required(self):
        self._get_product_calculation()
        if self.product_calculation:
            return '{0:.2f}'.format(self.product_calculation.capital_not_required)
        else:
            return ''

    def get_interest_required(self):
        self._get_product_calculation()
        if self.product_calculation:
            return '{0:.2f}'.format(self.product_calculation.interest_required)
        else:
            return ''

    def get_interest(self):
        self._get_product_calculation()
        if self.product_calculation:
            return '{0:.2f}'.format(self.product_calculation.interest_required)
        else:
            return ''

    def get_daily_interest(self):
        self._get_product_calculation()
        if self.product_calculation:
            return '{0:.2f}'.format(self.product_calculation.interest_required_daily)
        else:
            return ''

    def get_costs(self):
        self._get_product_calculation()
        if self.product_calculation:
            return '{0:.2f}'.format(self.product_calculation.cost)
        else:
            return ''

    def get_debtor_bank_account(self):
        return '11 2222 3333 4444 5555 6666 7777'

    def get_agreement_termination_period(self):
        return 7

    def get_client_name(self):
        return "%s %s" % (self.document.owner.first_name, self.document.owner.last_name)

    def get_client_address(self):
        if self.document.owner.is_company:
            address = self.document.owner.company_address
        else:
            address = self.document.owner.home_address
        if address:
            return address.get_compact_address(split_line=True)
        else:
            return ""
