from django.utils.translation import gettext_lazy as _
from django.db.models import JSONField
from django.db import models


class StatGroupAdviser(models.Model):
    name = models.CharField(verbose_name=_('stat.group.adviser.name'), max_length=200)
    advisers = JSONField(verbose_name=_('stat.group.adviser.advisers'), null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'stat_group_adviser'
        ordering = ['name']


class StatGroupLoanStatus(models.Model):
    name = models.CharField(verbose_name=_('stat.group.loan.name'), max_length=200)
    statuses = JSONField(verbose_name=_('stat.group.loan.statuses'), null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'stat_group_loan_status'
        ordering = ['name']
