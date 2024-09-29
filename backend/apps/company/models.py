from django.db import models
from django.utils.translation import gettext_lazy as _

from application.models import AuditMixin, AddressMixin, CompanyDataMixin, ContactDataMixin
from apps.user.models import User


class Company(AuditMixin, AddressMixin, CompanyDataMixin, ContactDataMixin, models.Model):
    name = models.CharField(verbose_name='company.name', max_length=200)
    establish_date = models.DateField(verbose_name=_('company.establish_date'), null=True, blank=True)
    legal_form = models.CharField(verbose_name=_('company.legal_form'), max_length=200, null=True, blank=True)
    description = models.TextField(verbose_name=_('company.description'), null=True, blank=True)
    activity_status = models.CharField(verbose_name=_('company.activity_status'), max_length=50, null=True, blank=True,
                                       choices=[('ACT', 'aktywna'), ('INACT', 'nieaktywna')])

    class Meta:
        db_table = 'company'


class CompanyManagement(AuditMixin, models.Model):
    ROLES = [
        ('chairman of the board', 'COB'),
        ('member of the board', 'MOB'),
        ('proxy', 'PRX')
    ]
    company = models.ForeignKey(Company, on_delete=models.CASCADE, db_column='id_company', related_name='company_management_set')
    manager = models.ForeignKey(User, on_delete=models.CASCADE, db_column='id_manager', null=True, blank=True)
    role = models.CharField(verbose_name=_('company_management.role'), max_length=100, choices=ROLES)
    description = models.TextField(verbose_name=_('company_management.description'), null=True, blank=True)

    class Meta:
        db_table = 'company_management'
