import datetime
from datetime import timedelta
from decimal import Decimal

from django.db.models import JSONField
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Max
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from application.models import AppModel
from apps.attachment.models import Attachment
from apps.attribute.models import Attribute
from apps.config.models import HoldingCompany
from apps.dict.models import DictionaryEntry
from apps.document.models import DocumentType, DocumentTypeAccountingType, Document, DocumentTypeStatus
from apps.hierarchy.models import Hierarchy
from apps.report.models import Report, ReportTemplate
from apps.scheduler.schedule.models import Schedule
from apps.user.models import User
from apps.user_func.adviser.models import Adviser
from apps.user_func.broker.models import Broker
from apps.user_func.client.models import Client, ClientFunction

INTEREST_FOR_DELAY_RATE_USE_DEFAULT = 'XXX'
INSTALMENT_INTEREST_CAPITAL_TYPE_CALC_SOURCE_DEFAULT = 'G'


class ProductAccounting(models.Model):
    product = models.ForeignKey('Product', db_column='id_product', on_delete=models.CASCADE)
    accounting_type = models.ForeignKey(DocumentTypeAccountingType, db_column='id_accounting_type',
                                        on_delete=models.CASCADE)
    sq = models.IntegerField()

    class Meta:
        db_table = 'product_accounting'
        default_permissions = ()


class ProductAttachment(models.Model):
    attachment_owner = models.ForeignKey('Product', db_column='id_product', on_delete=models.CASCADE)
    attachment = models.ForeignKey(Attachment, db_column='id_attachment', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.pk)

    class Meta:
        db_table = "product_attachment"
        default_permissions = ()


class Product(models.Model):
    document = models.OneToOneField(Document, db_column='id_document', null=True, blank=True, related_name='product',
                                    on_delete=models.CASCADE)  # TODO: Docelowo ustawić wymagalność po usunięciu produktów z bazy
    type = models.ForeignKey(DocumentType, db_column='id_type', on_delete=models.CASCADE)  # TODO: docelowo usunąć

    creditor = models.ForeignKey(Hierarchy, db_column='id_creditor', null=True, blank=True, related_name='creditor',
                                 on_delete=models.CASCADE)
    client = models.ForeignKey(Client, db_column='id_client', on_delete=models.CASCADE, related_name='product_set')
    adviser = models.ForeignKey(Adviser, db_column='id_adviser', null=True, blank=True, on_delete=models.CASCADE)
    broker = models.ForeignKey(Broker, db_column='id_broker', null=True, blank=True, on_delete=models.CASCADE)
    accounting = models.ManyToManyField(DocumentTypeAccountingType, through=ProductAccounting)
    agreement_no = models.CharField(verbose_name=_('product.agreement_no'), max_length=100, unique=True)

    start_date = models.DateField(verbose_name=_('product.start_date'))
    #  this date informs about the min date after system can revert statuses during re-calculating product

    end_date = models.DateField(verbose_name=_('product.end_date'), null=True, blank=True)
    termination_date = models.DateField(verbose_name=_('product.termination_date'), null=True, blank=True)
    capitalization_date = models.DateField(verbose_name=_('product.capitalization_date'), null=True, blank=True)
    creation_date = models.DateTimeField(verbose_name=_('product.creation_date'))

    creation_user = models.ForeignKey(User, verbose_name=_('product.creation_user'), related_name='creation_user',
                                      on_delete=models.CASCADE)

    status = models.ForeignKey('ProductTypeStatus', db_column='id_status', related_name='status_set',
                               on_delete=models.CASCADE)
    recount_required_date = models.DateField(verbose_name=_('product.recount_required_date'), null=True, blank=True)
    # recount_required_date_creation_marker: marker where the recount required date was set. It's when recount is done the date is set to null.
    # If during the recount process some other process set the value, the marker changes and thus recount proces would know
    # that it cannot clear the recount_required_date
    recount_required_date_creation_marker = models.DateTimeField(null=True, blank=True)
    attachments = models.ManyToManyField(Attachment, through=ProductAttachment)
    # accounting data
    creditor_bank_account = models.CharField(verbose_name=_('product.creditor_bank_account'), max_length=28, null=True,
                                             blank=True)
    debtor_bank_account = models.CharField(verbose_name=_('product.debtor_bank_account'), max_length=28, null=True,
                                           blank=True)

    value = models.DecimalField(verbose_name=_('product.value'), max_digits=10, decimal_places=2)
    balance = models.DecimalField(verbose_name=_('product.value'), max_digits=10, decimal_places=2, default=Decimal(-1))
    capital_net = models.DecimalField(verbose_name=_('product.capital_net'), max_digits=10, decimal_places=2, default=0)
    commission = models.DecimalField(verbose_name=_('product.commision'), max_digits=10, decimal_places=2, default=0)
    instalment_capital = models.DecimalField(verbose_name=_('product.instalment_capital'), max_digits=10,
                                             decimal_places=2, default=0)
    instalment_commission = models.DecimalField(verbose_name=_('product.instalment_commission'), max_digits=10,
                                                decimal_places=2, default=0)
    instalment_interest_rate = models.DecimalField(verbose_name=_('product.instalment_interest'), max_digits=10,
                                                   decimal_places=4, default=0)
    # count of days where interest for delay won't be calculated
    grace_period = models.IntegerField(verbose_name=_('product.grace_period'), default=0)
    debt_collection_fee_period = models.IntegerField(verbose_name=_('product.debt_collection_fee_period'), default=0)
    debt_collection_fee = models.DecimalField(verbose_name=_('product.debt_collection_fee'), max_digits=10,
                                              decimal_places=2, default=0)
    # interest type used in product daily calculation
    interest_for_delay_rate_use = models.CharField(verbose_name=_('product.interest_for_delay_rate_use'), max_length=10,
                                                   default=INTEREST_FOR_DELAY_RATE_USE_DEFAULT)
    interest_for_delay_type = models.SmallIntegerField(null=True, blank=True)

    # Interest for delay can ge calculated not always basing on capital required (although mostly). There are some specific loans where
    # the base for interest for delay calculation is greater than capital_required + nvl(commission_required, 0). the difference is constant.
    # EXAMPLE. capital_gross = 200 000,00. There is ie. deposit = 100 000,00. So the interest_for_delay_calculation_add_value = 100 000,00 that means
    # that total interest_for_delay_calculation_base = 300 000,00
    # total product value = 200 000,00
    # the difference is then 100 000,00
    # self.interest_for_delay_calculation_base is changing the same way as capital_required (CAP_REQ)
    interest_for_delay_calculation_add_value = models.DecimalField(
        verbose_name=_('product.interest_for_delay_calculation_add_value'), max_digits=10, decimal_places=2, default=0)

    # indicates if take either capital net or gross as initial CAP_NOT_REQ
    capital_type_calc_source = models.CharField(verbose_name=_('product.capital_type_calc_source'), max_length=10,
                                                default=INSTALMENT_INTEREST_CAPITAL_TYPE_CALC_SOURCE_DEFAULT)

    def __str__(self):
        return str(f'{self.pk}: {self.document}')

    class Meta:
        db_table = 'product'
        default_permissions = ()
        permissions = (
            ('add:all', _('product.permissions.add.all')),
            ('add:own', _('product.permissions.add.own')),

            ('change:all', _('product.permissions.change.all')),
            ('change:own', _('product.permissions.change.own')),

            ('list:all', _('product.permissions.list.all')),
            ('list:own', _('product.permissions.list.own')),

            ('view:all', _('product.permissions.view.all')),
            ('view:own', _('product.permissions.view.own')),
        )


class ProductTranche(AppModel):
    product = models.ForeignKey(Product, db_column='id_product', related_name='tranches', on_delete=models.CASCADE)
    title = models.CharField(verbose_name=_('title'), max_length=255)
    lender = models.ForeignKey(Hierarchy, db_column='id_lender', related_name='tranche_lender',
                               on_delete=models.CASCADE)
    condition = models.TextField(verbose_name=_('condition'), null=True, blank=True)
    value = models.DecimalField(verbose_name=_('value'), max_digits=10, decimal_places=2)
    launch_date = models.DateField(null=True, blank=True)
    sq = models.SmallIntegerField(verbose_name=_('sq'))

    class Meta:
        db_table = 'product_tranche'


class ProductClient(models.Model):
    product = models.ForeignKey(Product, db_column='id_product', related_name='client_set', on_delete=models.CASCADE)
    client = models.ForeignKey(Client, db_column='id_client', on_delete=models.CASCADE)
    function = models.ForeignKey(ClientFunction, verbose_name=_('product.client.function'), db_column='id_function',
                                 on_delete=models.CASCADE)

    class Meta:
        db_table = 'product_client'
        default_permissions = ()


class ProductSchedule(models.Model):
    product = models.ForeignKey('Product', db_column='id_product', related_name='schedule_set',
                                on_delete=models.CASCADE)
    maturity_date = models.DateField()
    instalment_capital = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    instalment_interest = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    instalment_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    instalment_total = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)

    def __str__(self):
        return str(self.pk)

    class Meta:
        db_table = "product_schedule"
        default_permissions = ()


class ProductCashFlow(models.Model):
    product = models.ForeignKey(Product, db_column='id_product', related_name='cashflow_set', on_delete=models.CASCADE)
    transaction_uid = models.CharField(max_length=100, null=True, blank=True)
    type = models.ForeignKey(DocumentTypeAccountingType, db_column='id_type', on_delete=models.CASCADE)
    # additional distinction of the kind of accounting
    subtype = models.CharField(max_length=10, null=True, blank=True)
    value = models.DecimalField(verbose_name=_('product.cash.flow.value'), max_digits=10, decimal_places=2)
    # data efektywna - ważna dla algorytmu, bo wg niej rozliczenia
    cash_flow_date = models.DateField(verbose_name=_('product.cash.flow.cash_flow_date'), null=True, blank=True)
    # data faktycznego "fizycznego" zaksięgowania. Różnice będą dla kosztów, bo koszty księgowane z inną datą niż faktycznie powstały. Zwykle na końcu umowy
    accounting_date = models.DateField(verbose_name=_('product.cash.flow.accounting_date'), null=True, blank=True)
    entry_source = models.CharField(verbose_name=_('product.cash.flow.entry_source'), default='HAND', max_length=10)
    description = models.CharField(max_length=500, null=True, blank=True)
    editable = models.BooleanField(default=True)
    calculable = models.BooleanField(default=True)

    class Meta:
        db_table = 'product_cash_flow'
        default_permissions = ()


class ProductActionAttachment(models.Model):
    product = models.ForeignKey('ProductAction', db_column='id_product', on_delete=models.CASCADE)
    attachment = models.ForeignKey(Attachment, db_column='id_attachment', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.pk)

    class Meta:
        db_table = "product_action_attachment"
        default_permissions = ()


class ProductActionDefinition(models.Model):
    document_type = models.ForeignKey(DocumentType, db_column='id_document_type', null=True, blank=True,
                                      on_delete=models.CASCADE)
    report = models.ForeignKey(ReportTemplate, db_column='id_report', null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=300, verbose_name=_('product.action.definition.name'))
    sq = models.IntegerField()

    class Meta:
        db_table = "product_action_definition"


class ProductTypeAction(models.Model):
    product = models.ForeignKey(Product, db_column='id_product', on_delete=models.CASCADE)
    action = models.ForeignKey(ProductActionDefinition, db_column='id_action', on_delete=models.CASCADE)
    sq = models.IntegerField()

    class Meta:
        db_table = "product_type_action"
        default_permissions = ()


class ProductAction(models.Model):
    product = models.ForeignKey(Product, db_column='id_product', related_name='action_set', on_delete=models.CASCADE)
    action = models.ForeignKey(ProductActionDefinition, db_column='id_action', null=True, blank=True,
                               on_delete=models.CASCADE)
    report = models.ForeignKey(Report, db_column='id_report', null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=300, verbose_name=_('product.action.name'))
    description = models.CharField(verbose_name=_('product.action.description'), max_length=500, null=True, blank=True)
    cost = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('product.action.cost'), blank=True,
                               null=True)
    send_date = models.DateField(verbose_name=_('product.action.send_date'), blank=True, null=True)
    receive_date = models.DateField(verbose_name=_('product.action.receive_date'), blank=True, null=True)
    action_date = models.DateTimeField(verbose_name=_('product.action.action_date'))
    action_execution_date = models.DateField(verbose_name=_('product.action.action_execution_date'), null=True)
    created_by = models.ForeignKey(User, db_column='id_created_by', on_delete=models.CASCADE)
    attachments = models.ManyToManyField(Attachment, through=ProductActionAttachment)
    datasource = JSONField(null=True)

    class Meta:
        db_table = 'product_action'
        default_permissions = ()


class ProductInterestType(models.Model):
    name = models.CharField(verbose_name='product.interest.type.name', max_length=100)
    code = models.CharField(verbose_name='product.interest.type.code', max_length=100, unique=True)
    description = models.TextField(verbose_name='product.interest.type.description', null=True, blank=True)

    # todo: it can be only one is_default option set to True. Need to make it dependent on document type
    is_default = models.BooleanField(verbose_name='product.interest.type.is_default', default=False)
    sq = models.IntegerField(db_column='sq')

    def __str__(self):
        return str(self.name)

    @staticmethod
    def get_default():
        try:
            return ProductInterestType.objects.get(is_default=True)
        except ProductInterestType.DoesNotExist:
            return None

    class Meta:
        db_table = 'product_interest_type'
        default_permissions = ()
        ordering = ['sq']


class ProductInterest(models.Model):
    product = models.ForeignKey(Product, db_column='id_product', related_name='interest_set', on_delete=models.CASCADE)
    type = models.ForeignKey(ProductInterestType, verbose_name=_('product.interest.type'), db_column='id_type',
                             related_name='type', on_delete=models.CASCADE)
    start_date = models.DateField(verbose_name=_('product.interest.start_date'))
    delay_rate = models.DecimalField(verbose_name=_('product.interest.delay_rate'), max_digits=10, decimal_places=4)
    delay_max_rate = models.DecimalField(verbose_name=_('product.interest.delay_max_rate'), max_digits=10,
                                         decimal_places=4)
    statutory_rate = models.DecimalField(verbose_name=_('product.interest.statutory_rate'), max_digits=10,
                                         decimal_places=4)
    is_set_globally = models.BooleanField(verbose_name=_('product.interest.is_set_globally'), default=False)
    history = HistoricalRecords(table_name='h_product_interest')

    class Meta:
        db_table = "product_interest"
        default_permissions = ()


class ProductInterestGlobal(models.Model):
    interest_list = None

    document_type = models.ForeignKey(DocumentType,
                                      verbose_name=_('product.interest.global.document_type'),
                                      db_column='id_document_type',
                                      on_delete=models.CASCADE)
    start_date = models.DateField(verbose_name=_('product.interest.global.start_date'), unique=True)
    interest_for_delay_rate = models.DecimalField(verbose_name=_('product.interest.global.interest_for_delay_rate'),
                                                  max_digits=10, decimal_places=4)
    interest_max_for_delay_rate = models.DecimalField(
        verbose_name=_('product.interest.global.interest_max_for_delay_rate'),
        max_digits=10, decimal_places=4)
    creation_date = models.DateTimeField(verbose_name=_('product.interest.global.creation_date'), auto_now_add=True)
    created_by = models.ForeignKey(User, verbose_name=_('product.interest.global.created_by'),
                                   db_column='id_created_by',
                                   related_name='interest_global_created_by',
                                   on_delete=models.CASCADE)

    class Meta:
        db_table = 'product_interest_global'
        default_permissions = ()

    @classmethod
    def get_list(cls):
        return list(cls.objects.all().order_by('start_date'))

    @classmethod
    def get_for(cls, date: datetime.date):
        if cls.interest_list is None:
            cls.interest_list = cls.get_list()

        if cls.interest_list is None or len(cls.interest_list) == 0:
            return 0.0, 0.0

        interest = cls.interest_list[0]

        if interest.start_date > date:
            return 0.0, 0.0

        elif len(cls.interest_list) == 1:
            return interest.interest_for_delay_rate, interest.interest_max_for_delay_rate

        for i in cls.interest_list[1:]:
            if i.start_date > date:
                return interest.interest_for_delay_rate, interest.interest_max_for_delay_rate
            if i.start_date == date:
                return i.interest_for_delay_rate, i.interest_max_for_delay_rate
            interest = i

        return interest.interest_for_delay_rate, interest.interest_max_for_delay_rate


class ProductCalculation(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    product = models.ForeignKey(Product, db_column='id_product', related_name='calculation', on_delete=models.CASCADE)
    # snapshot of the document status valid for calculation day. Needed for recalcultion. When recalculating,
    # document status is initially rolled back to that which was day the recalculation starts on
    product_status = models.ForeignKey('ProductTypeStatus', db_column='id_product_type_status',
                                       on_delete=models.CASCADE)
    calc_date = models.DateField(verbose_name='product.calculation.calc_date')

    # Saldo
    balance = models.DecimalField(verbose_name='product.calculation.capital_per_day', max_digits=15, decimal_places=2,
                                  default=0)

    # kapitał
    capital_per_day = models.DecimalField(verbose_name='product.calculation.capital_per_day', max_digits=15,
                                          decimal_places=2, default=0)
    capital_not_required = models.DecimalField(verbose_name='product.calculation.capital_not_required', max_digits=15,
                                               decimal_places=2, default=0)
    capital_required = models.DecimalField(verbose_name='product.calculation.capital_required', max_digits=15,
                                           decimal_places=2, default=0)
    capital_required_from_schedule = models.DecimalField(
        verbose_name='product.calculation.capital_required_from_schedule', max_digits=15, decimal_places=2)

    #  rata odsetkowa
    interest_daily = models.DecimalField(verbose_name='product.calculation.interest_daily', max_digits=15,
                                         decimal_places=2, default=0)
    interest_per_day = models.DecimalField(verbose_name='product.calculation.interest_per_day', max_digits=15,
                                           decimal_places=2, default=0)
    interest_cumulated_per_day = models.DecimalField(
        verbose_name='product.calculation.interest_cumulated_per_day', max_digits=15, decimal_places=2, default=0
    )
    interest_required = models.DecimalField(verbose_name='product.calculation.interest_required', max_digits=15,
                                            decimal_places=2, default=0)
    interest_required_from_schedule = models.DecimalField(
        verbose_name='product.calculation.interest_required_from_schedule', max_digits=15, decimal_places=2, default=0)
    interest_rate = models.DecimalField(verbose_name='product.calculation.interest_rate', max_digits=10,
                                        decimal_places=2, null=True, default=0)

    # odsetki za opóźnienie
    interest_for_delay_calculation_base = models.DecimalField(
        verbose_name='product.calculation.interest_for_delay_calculation_base', max_digits=15, decimal_places=2,
        default=0)
    interest_for_delay_total = models.DecimalField(verbose_name='product.calculation.interest_for_delay_total',
                                                   max_digits=15, decimal_places=2, default=0)
    interest_for_delay_rate = models.DecimalField(verbose_name='product.calculation.interest_for_delay_rate',
                                                  max_digits=10, decimal_places=2, null=True, default=0)
    interest_for_delay_required = models.DecimalField(verbose_name='product.calculation.interest_for_delay_required',
                                                      max_digits=15, decimal_places=2, default=0)
    interest_for_delay_required_daily = models.DecimalField(
        verbose_name='product.calculation.interest_for_delay_required_daily', max_digits=15, decimal_places=2,
        default=0)

    # prowizja
    commission_per_day = models.DecimalField(verbose_name='product.calculation.commission_per_day', max_digits=15,
                                             decimal_places=2, default=0)
    commission_required = models.DecimalField(verbose_name='product.calculation.commission_required', max_digits=15,
                                              decimal_places=2, default=0)
    commission_not_required = models.DecimalField(verbose_name='product.calculation.commission_total', max_digits=15,
                                                  decimal_places=2, default=0)
    commission_required_from_schedule = models.DecimalField(
        verbose_name='product.calculation.commission_required_from_schedule', max_digits=15, decimal_places=2,
        default=0)

    # suma zobowiązań capital_required + interest_required + commission_required
    required_liabilities_sum = models.DecimalField(verbose_name='product.calculation.required_liabilities_sum',
                                                   max_digits=15, decimal_places=2, default=0)
    required_liabilities_sum_from_schedule = models.DecimalField(
        verbose_name='product.calculation.required_liabilities_sum_from_schedule', max_digits=15, decimal_places=2,
        default=0)

    # koszt wystąpienie w danym dniu
    cost_occurrence = models.DecimalField(verbose_name='product.calculation.cost_occurence', max_digits=15,
                                          decimal_places=2, default=0)

    # koszt - stan na dzień
    cost = models.DecimalField(verbose_name='product.calculation.interest_required_daily', max_digits=15,
                               decimal_places=2, default=0)

    # kosz suma
    cost_total = models.DecimalField(verbose_name='product.calculation.cost_total', max_digits=15, decimal_places=2,
                                     default=0)

    #  wpłata
    instalment = models.DecimalField(verbose_name='product.calculation.instalment', max_digits=15, decimal_places=2,
                                     default=0)
    instalment_total = models.DecimalField(verbose_name='product.calculation.instalment_total', max_digits=15,
                                           decimal_places=2, default=0)
    instalment_overpaid = models.DecimalField(verbose_name='product.calculation.instalment_overpaid', max_digits=15,
                                              decimal_places=2, default=0)

    # rozksięgowanie raty na poszczególne składniki
    instalment_accounting_capital_required = models.DecimalField(
        verbose_name='product.calculation.instalment_capital_required', max_digits=15, decimal_places=2, default=0)
    instalment_accounting_capital_not_required = models.DecimalField(
        verbose_name='product.calculation.instalment_capital_not_required', max_digits=15, decimal_places=2, default=0)
    instalment_accounting_commission_required = models.DecimalField(
        verbose_name='product.calculation.instalment_commission_required', max_digits=15, decimal_places=2, default=0)
    instalment_accounting_commission_not_required = models.DecimalField(
        verbose_name='product.calculation.instalment_commission_not_required', max_digits=15, decimal_places=2,
        default=0)
    instalment_accounting_interest_required = models.DecimalField(
        verbose_name='product.calculation.instalment_interest_required', max_digits=15, decimal_places=2, default=0)
    instalment_accounting_interest_for_delay = models.DecimalField(
        verbose_name='product.calculation.instalment_instalment_interest', max_digits=15, decimal_places=2, default=0)
    instalment_accounting_cost = models.DecimalField(verbose_name='product.calculation.instalment_cost', max_digits=15,
                                                     decimal_places=2)

    # liczba kolejnych przeterminowanych
    instalment_overdue_count = models.IntegerField(default=0)
    # liczba wystąpień przeterminowania
    instalment_overdue_occurrence = models.IntegerField(default=0)

    # Umorzenia
    remission_capital = models.DecimalField(verbose_name='product.calculation.remission_capital', max_digits=15,
                                            decimal_places=2, default=0)
    remission_commission = models.DecimalField(verbose_name='product.calculation.remission_commission', max_digits=15,
                                               decimal_places=2, default=0)
    remission_interest = models.DecimalField(verbose_name='product.calculation.remission_interest', max_digits=15,
                                             decimal_places=2, default=0)
    remission_interest_for_delay = models.DecimalField(verbose_name='product.calculation.remission_interest_for_delay',
                                                       max_digits=15, decimal_places=2, default=0)
    remission_cost = models.DecimalField(verbose_name='product.calculation.remission_cost', max_digits=15,
                                         decimal_places=2, default=0)

    @staticmethod
    def get_max_calculation_date(product):
        return ProductCalculation.objects.filter(
            product=product).aggregate(Max('calc_date'))['calc_date__max'] + timedelta(days=1)

    class Meta:
        db_table = 'product_calculation'
        default_permissions = ()


class ProductTypeCommission(models.Model):
    document_type = models.ForeignKey(to=DocumentType, db_column='id_document_type', on_delete=models.CASCADE,
                                      related_name='commission_set')
    name = models.CharField(verbose_name=_('product.type.commission.name'), max_length=200)
    # procentowa lub kwotowa [PRC, CSH]
    type = models.CharField(verbose_name=_('product.type.commission.type'), max_length=3)
    # [IN, OUT] => jednorazowa. Jeżeli kwotowa, to kwota, jeżeli procentowa, to od ???? [MC, QR, YR] => cykliczna
    period = models.CharField(verbose_name=_('product.type.commission.period'), max_length=3)
    # liczona od:
    #      - saldo na dany dzień => DAY_BALANCE (PRC)
    #      - średnia arytmetyczna od zaangażowanego kapitału na dany okres określony w period => [MC, QR, YR] CAPITAL_INVOLVED (PRC)
    #      - od niewykorzystanego / potencjalnego salda - za gotowość okres określony w period => [MC, QR, YR] CAPITAL_UNUSED (PRC)
    #      - KWOTOWA niezależna od kapitału (CSH)
    #
    calculation_type = models.CharField(verbose_name=_('product.type.commission.calculation_type'), max_length=20)
    # jeżeli calculation_type procentowa, to procent, jeżeli kwotowa, to kwota
    default_value = models.DecimalField(
        verbose_name=_('product.type.commission.default_value'),
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'product_type_commission'
        default_permissions = ()


class ProductCommission(models.Model):
    product = models.ForeignKey(to=Product, db_column='id_product', on_delete=models.CASCADE,
                                related_name='commission_set')
    commission = models.ForeignKey(to=ProductTypeCommission, db_column='id_commission', on_delete=models.CASCADE,
                                   related_name='product_set')
    value = models.DecimalField(verbose_name=_('product.commission.value'), max_digits=15, decimal_places=2)
    name = models.CharField(verbose_name=_('product.commission.name'), max_length=200, null=True, blank=True)
    description = models.TextField(verbose_name=_('product.commission.name'), null=True, blank=True)
    is_active = models.BooleanField(verbose_name=_('product.commission.is_active'), default=True)
    date_from = models.DateField(verbose_name=_('product.commission.date_from'), null=True, blank=True)
    date_to = models.DateField(verbose_name=_('product.commission.date_to'), null=True, blank=True)

    # sq = models.IntegerField(verbose_name=_('product.commissiom.sq'))

    class Meta:
        db_table = 'product_commission'
        default_permissions = ()


class ProductTypeStatus(models.Model):
    type = models.ForeignKey(DocumentType, db_column='id_type', related_name='product_status_set',
                             on_delete=models.CASCADE)
    name = models.CharField(verbose_name=_('product.type.status.name'), max_length=100)
    code = models.CharField(verbose_name=_('product.type.status.code'), max_length=10)
    is_initial = models.BooleanField(verbose_name=_('product.type.status.is_initial'))
    is_active = models.BooleanField(verbose_name=_('product.type.status.is_active'), default=True)
    is_alternate = models.BooleanField(verbose_name=_('product.type.status.is_alternate'), default=False)
    is_closing_process = models.BooleanField(verbose_name=_('product.type.status.is_closing_process'), default=False)
    action_class = models.CharField(max_length=300, null=True, blank=True)
    action = models.CharField(max_length=300, null=True, blank=True)
    color = models.CharField(verbose_name=_('document.type.status.can_revert'), max_length=8, default='ffffff')
    sq = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'product_type_status'


class ProductTypeProcessFlow(models.Model):
    status = models.ForeignKey(ProductTypeStatus, db_column='id_current_status', related_name='status',
                               on_delete=models.CASCADE)
    available_status = models.ForeignKey(ProductTypeStatus, db_column='id_available_status', null=True, blank=True,
                                         related_name='available_status', on_delete=models.CASCADE)
    is_default = models.BooleanField(default=False)
    sq = models.IntegerField()

    class Meta:
        db_table = 'product_type_process_flow'


class ProductStatusTrack(models.Model):
    """
    DocumentStatusTrack
    track all the status changes of given document with chance to descripbe reason of change
    """
    product = models.ForeignKey(Product, db_column='id_product', db_index=True, related_name='status_track_set',
                                on_delete=models.CASCADE)
    status = models.ForeignKey(ProductTypeStatus, db_column='id_status', db_index=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, db_column='id_created_by', on_delete=models.CASCADE)
    effective_date = models.DateTimeField(default=timezone.now)
    creation_date = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(null=True)
    is_initial = models.BooleanField(default=False)

    class Meta:
        db_table = 'product_status_track'


class CompanyBankTransactionFile(models.Model):
    company = models.OneToOneField(Hierarchy, primary_key=True, db_column='id_company',
                                   related_name='bank_transaction_file', on_delete=models.CASCADE)
    base_dir = models.CharField(max_length=200, default='')
    subdir = models.CharField(max_length=200, default='')

    # @classmethod
    # def get_subsidiary_companies(cls):
    #     return {i.company.name: i.base_dir for i in cls.objects.all()}

    class Meta:
        db_table = 'product_company_bank_transaction_file'
