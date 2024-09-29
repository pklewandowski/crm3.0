
from django.utils.translation import gettext_lazy as _
from django.db import models

from apps.config.models import HoldingCompany
from apps.user.models import User
from apps.user_func.adviser.models import Adviser
from apps.user_func.broker.models import Broker
from apps.dict.models import DictionaryEntry
from apps.document.models import DocumentType
from apps.dict.models import DictionaryEntry
from simple_history.models import HistoricalRecords


class ProcessingAgreement(models.Model):
    name = models.CharField(verbose_name=_('processing_agreement.name'), max_length=200)
    code = models.CharField(verbose_name=_('processing_agreement.code'), max_length=30)
    type = models.CharField(verbose_name=_('processing_agreement.type'), max_length=3)
    text = models.TextField(verbose_name=_('processing_agreement.text'))
    active = models.BooleanField(verbose_name=_('processing_agreement.active'), default=True)
    required = models.BooleanField(verbose_name=_('processing_agreement.required'), default=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    confirmation_date = models.DateTimeField()
    confirmed_by = models.ForeignKey(User, db_column='id_confirmed_by', on_delete=models.PROTECT)
    sq = models.IntegerField(verbose_name=_('processing_agreement.sq'), default=0)
    history = HistoricalRecords(table_name='h_processing_agreement')

    def __str__(self):
        return self.text

    class Meta:
        db_table = 'processing_agreement'


class ClientProcessingAgreement(models.Model):
    client = models.ForeignKey('Client', db_column='id_client', related_name='processing_agreement_set', on_delete=models.CASCADE)
    # jeśli zgoda zatwierdzona, to nie można zmienić jej treści. Należy stworzyć nową zgodę z nową treścią
    processing_agreement = models.ForeignKey(ProcessingAgreement, db_column='id_processing_agreement', on_delete=models.CASCADE)
    text = models.TextField()
    source = models.CharField(max_length=10)
    value = models.BooleanField()
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(null=True, blank=True)
    history = HistoricalRecords(table_name='h_client_processing_agreement')

    class Meta:
        db_table = 'client_processing_agreement'


class Client(models.Model):
    STATUS_DEFAULT = 'IN'
    STATUS = (
        (STATUS_DEFAULT, 'In'),
        ('OUT', 'Out'),
        ('PROSPECT', 'Prospect'),
        ('INVEST', 'Inwestycje / Pożyczka')
    )

    SOURCE = (
        ('', '----'),
        ('WL', 'Własne'),
        ('POL', 'Polecenie'),
        ('CC', 'CC'),
        ('BRK', 'Pośrednik'),
        ('WK', 'Walk in')
    )

    STATUS_DICT = dict(STATUS)
    SOURCE_DICT = dict(SOURCE)

    user = models.OneToOneField(User, verbose_name=_('client.user'), primary_key=True, db_column='id', related_name='client', on_delete=models.CASCADE)
    document_type = models.ForeignKey(DocumentType, db_column='id_document_type', on_delete=models.CASCADE)
    adviser = models.ForeignKey(Adviser, db_column='id_adviser', verbose_name=_('client.adviser'), null=True, blank=True, related_name='client_adviser', on_delete=models.CASCADE)
    broker = models.ForeignKey(Broker, db_column='id_broker', verbose_name=_('client.broker'), null=True, blank=True, related_name='client_broker', on_delete=models.CASCADE)
    company = models.ForeignKey(HoldingCompany, db_column='id_company', verbose_name=_('client.company'), null=True, blank=True, related_name='company', on_delete=models.CASCADE)
    processing_agreement = models.ManyToManyField(ProcessingAgreement, through=ClientProcessingAgreement)
    status = models.CharField(verbose_name=_('client.status'), max_length=10, choices=STATUS, default=STATUS_DEFAULT)
    source = models.CharField(verbose_name=_('client.source'), max_length=200, choices=SOURCE, null=True, blank=True)

    def __str__(self):
        return (self.user.first_name or '') + ' ' + (self.user.last_name or '')

    def get_status_label(self):
        return self.STATUS_DICT[self.status] if self.status in self.STATUS_DICT else ''

    def get_source_label(self):
        return self.SOURCE_DICT[self.source] if self.source in self.SOURCE_DICT else ''

    class Meta:
        db_table = "user_client"
        default_permissions = ()
        permissions = (
            ('add:all', _('permissions.app.user.client.add.all')),
            ('add:department', _('permissions.app.user.client.add.department')),
            ('add:own', _('permissions.app.user.client.add.own')),

            ('list:all', _('permissions.app.user.client.list.all')),
            ('list:department', _('permissions.app.user.client.list.department')),
            ('list:own', _('permissions.app.user.client.list.own')),

            ('change:all', _('permissions.app.user.client.change.all')),
            ('change:department', _('permissions.app.user.client.change.department')),
            ('change:own', _('permissions.app.user.client.change.own')),
        )


class ClientFunction(models.Model):
    name = models.CharField(verbose_name=_('client.function.name'), max_length=200)
    sq = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = "client_function"


class ClientAccessToken(models.Model):
    client = models.ForeignKey(Client, db_column='id_client', on_delete=models.CASCADE)
    token = models.CharField(verbose_name=_('client_access_token.token'), max_length=500)
    valid = models.BooleanField(verbose_name=_('client_access_token.valid'), default=True)

    class Meta:
        db_table = "client_access_token"
