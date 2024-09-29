from django.utils.translation import gettext_lazy as _
from django.db import models

from apps.financial_accounting.batch_processing.models import File


class Transaction(models.Model):
    account_from = models.CharField(verbose_name='transaction.account_from', max_length=28)
    account_to = models.CharField(verbose_name='transaction.account_to', max_length=28)
    account_name_from = models.CharField(verbose_name='transaction.account_name_from', max_length=500, null=True, blank=True)
    account_name_to = models.CharField(verbose_name='transaction.account_name_to', max_length=500, null=True, blank=True)
    v_account_iph = models.CharField(verbose_name='transaction.v_account_iph', max_length=28, null=True, blank=True)
    title = models.CharField(verbose_name='transaction.title', max_length=500, null=True, blank=True)
    value = models.DecimalField(verbose_name='transaction.value', max_digits=15, decimal_places=2)
    transaction_no = models.CharField(verbose_name='transaction.transaction_number', max_length=50)
    transaction_date = models.DateField(verbose_name='transaction.transaction_date')
    accounting_date = models.DateField(verbose_name='transaction.accounting_date')
    source_name = models.CharField(verbose_name='transaction.source_name', max_length=50)
    source_type = models.CharField(verbose_name='transaction.source_type', max_length=20)
    source_filename = models.CharField(verbose_name='transaction.source_filename', max_length=300, null=True, blank=True)
    source_file_type = models.CharField(verbose_name='transaction.source_filetype', max_length=50)
    file = models.ForeignKey(File, on_delete=models.CASCADE, db_column='id_file', null=True, blank=True)
    destination_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'fa_transaction'
        constraints = [
            models.UniqueConstraint(fields=['transaction_no', 'source_name'], name='unique_trn_no_source_name')
        ]
