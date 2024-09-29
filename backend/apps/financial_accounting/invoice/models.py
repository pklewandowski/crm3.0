from django.utils.translation import gettext_lazy as _
from django.db import models
from django.core import validators

from apps.attachment.models import Attachment
from apps.document.models import Document
from apps.hierarchy.models import Hierarchy
from apps.user.models import User


class Invoice(models.Model):
    document = models.OneToOneField(Document, db_column='id_document', on_delete=models.CASCADE)
    number = models.CharField(verbose_name=_('invoice.number'), max_length=300)
    issuer = models.CharField(verbose_name=_('invoice.issuer'), max_length=500)
    recipient = models.CharField(verbose_name=_('invoice.recipient'), max_length=500)
    file_name = models.CharField(verbose_name=_('invoice.file_name'), max_length=300, null=True, blank=True)
    type = models.CharField(verbose_name=_('invoice.type'), max_length=20)  # , [I]incomming or [O]outgoing
    description = models.TextField(verbose_name=_('invoice.description'), null=True, blank=True)
    attachments = models.ManyToManyField(Attachment, through='InvoiceAttachment')

    def __str__(self):
        return self.number

    class Meta:
        db_table = 'fa_invoice'
        default_permissions = ('add', 'change')
        # permissions = ()


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, db_column='id_invoice', related_name='item_set', blank=True, on_delete=models.CASCADE)
    name = models.CharField(verbose_name=_('invoice.item.name'), max_length=500)
    code = models.CharField(verbose_name=_('invoice.item.code'), max_length=20, null=True, blank=True)
    quantity = models.DecimalField(verbose_name=_('invoice.item.quantity'), max_digits=15, decimal_places=2,
                                   validators=[validators.MinValueValidator(0)])
    unit_price = models.DecimalField(verbose_name=_('invoice.item.unit_price'), max_digits=15, decimal_places=2,
                                     validators=[validators.MinValueValidator(0)])
    unit_of_measure = models.CharField(verbose_name=_('invoice.item.unit_of_measure'), max_length=50)
    tax_value = models.DecimalField(verbose_name=_('invoice.item.tax_value'), max_digits=15, decimal_places=2)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'fa_invoice_item'


class InvoiceExtraItem(models.Model):
    invoice = models.ForeignKey(Invoice, db_column='id_invoice', related_name='extra_item_set', blank=True, on_delete=models.CASCADE)
    name = models.CharField(verbose_name=_('invoice.extra.item.name'), max_length=500)
    value = models.DecimalField(verbose_name=_('invoice.extra.item.value'), max_digits=15, decimal_places=2, validators=[validators.MinValueValidator(0)])

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'fa_invoice_extra_item'


class InvoiceAttachment(models.Model):
    invoice = models.ForeignKey(Invoice, db_column='id_invoice', on_delete=models.CASCADE)
    attachment = models.ForeignKey(Attachment, db_column='id_attachment', on_delete=models.CASCADE)

    class Meta:
        db_table = 'fa_invoice_attachment'
