from django.utils.translation import gettext_lazy as _
from django.db import models

from apps.document.models import Document
from apps.user_func.adviser.models import Adviser
from apps.user_func.broker.models import Broker
from apps.user_func.client.models import Client


class PartnerLead(models.Model):
    CLOSE_STATUS = 'CL'
    first_name = models.CharField(verbose_name=_('parnter.lead.first_name'), max_length=200, null=True)
    last_name = models.CharField(verbose_name=_('parnter.lead.last_name'), max_length=200, null=True)
    company_name = models.CharField(verbose_name=_('parnter.lead.company_name'), max_length=300, null=True)
    nip = models.CharField(verbose_name=_('parnter.lead.nip'), max_length=20, null=True)
    phone = models.CharField(verbose_name=_('parnter.lead.phone'), max_length=20, null=True)
    email = models.EmailField(verbose_name=_('parnter.lead.email'), null=True, db_index=True)
    amount = models.IntegerField(verbose_name=_('parnter.lead.amount'), null=True)
    period = models.IntegerField(verbose_name=_('parnter.lead.period'), null=True, blank=True)
    security_type = models.ForeignKey(to='PartnerSecurityType', verbose_name=_('parnter.lead.security_type'), null=True, on_delete=models.CASCADE)
    security_location = models.CharField(verbose_name=_('parnter.lead.security_location_city'), max_length=200, null=True)
    partner_first_name = models.CharField(verbose_name=_('parnter.lead.partner_first_name'), max_length=200, null=True)
    partner_last_name = models.CharField(verbose_name=_('parnter.lead.partner_last_name'), max_length=200, null=True)
    partner_phone = models.CharField(verbose_name=_('parnter.lead.partner_phone'), max_length=20, null=True)
    partner_email = models.EmailField(verbose_name=_('parnter.lead.partner_email'), null=True)
    agreements = models.ManyToManyField(verbose_name=_('parnter.lead.agreements'), to='PartnerAgreement', through='PartnerLeadAgreement', blank=True)
    adviser = models.ForeignKey(Adviser, db_column='id_adviser', null=True, blank=True, on_delete=models.CASCADE)
    broker = models.ForeignKey(Broker, db_column='id_broker', null=True, blank=True, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, db_column='id_client', null=True, blank=True, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, db_column='id_document', null=True, blank=True, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(verbose_name=_('parnter.lead.creation_date'), auto_now_add=True)
    status = models.CharField(verbose_name=_('parnter.lead.creation_date'), max_length=10, default='NW', blank=True)
    prefered_adviser_email = models.EmailField(verbose_name=_('parnter.lead.prefered_adviser_email'), null=True, blank=True)
    mortgage_register_no = models.CharField(verbose_name=_('parnter.lead.mortgage_register_no'), max_length=50, null=True, blank=True)

    def clean(self):
        for field in self._meta.fields:
            if isinstance(field, (models.CharField, models.TextField)):
                value = getattr(self, field.name)
                if value:
                    setattr(self, field.name, value.strip())

    class Meta:
        db_table = 'partner_lead'
        default_permissions = ()
        permissions = (
            ('view:all', _('permissions.app.partner.lead.view.all')),
            ('view:department', _('permissions.app.partner.lead.view.department')),
            ('view:position', _('permissions.app.partner.lead.view.position')),
            ('view:own', _('permissions.app.partner.lead.view.own')),

            ('list:all', _('permissions.app.partner.lead.list.all')),
            ('list:department', _('permissions.app.partner.lead.list.department')),
            ('list:position', _('permissions.app.partner.lead.list.position')),
            ('list:own', _('permissions.app.partner.lead.list.own')),

            ('add:all', _('permissions.app.partner.lead.add.all')),
            ('add:department', _('permissions.app.partner.lead.add.department')),
            ('add:position', _('permissions.app.partner.lead.add.position')),
            ('add:own', _('permissions.app.partner.lead.add.own')),

            ('change:all', _('permissions.app.partner.lead.change.all')),
            ('change:department', _('permissions.app.partner.lead.change.department')),
            ('change:position', _('permissions.app.partner.lead.change.position')),
            ('change:own', _('permissions.app.partner.lead.change.own')),
        )



class PartnerAgreement(models.Model):
    code = models.CharField(max_length=50)
    version = models.CharField(max_length=20)
    text = models.TextField()
    is_active = models.BooleanField(default=True)
    is_required = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100)
    sq = models.IntegerField()

    class Meta:
        db_table = 'partner_agreement'
        unique_together = ('code', 'version')


class PartnerLeadAgreement(models.Model):
    lead = models.ForeignKey(to=PartnerLead, db_column='id_lead', on_delete=models.CASCADE, related_name='agreement_set')
    agreement = models.ForeignKey(to=PartnerAgreement, db_column='id_agreement', on_delete=models.CASCADE)
    is_checked = models.BooleanField(default=False)
    check_date = models.DateTimeField(null=True)

    class Meta:
        db_table = 'partner_lead_agreement'
        ordering = ('agreement__sq',)


class PartnerSecurityType(models.Model):
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    sq = models.IntegerField()

    class Meta:
        db_table = 'partner_security_type'
