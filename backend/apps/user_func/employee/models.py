from django.utils.translation import gettext_lazy as _
from django.db import models
from apps.user.models import User
from apps.attachment.models import Attachment
from apps.document.models import DocumentType


class EmployeeContractType(models.Model):
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    part_time = models.BooleanField(default=False, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'employee_contract_type'


class EmployeeContract(models.Model):
    employee = models.ForeignKey('Employee', db_column='id_employee', on_delete=models.CASCADE)
    type = models.ForeignKey(EmployeeContractType, db_column='id_type', on_delete=models.CASCADE)
    code = models.CharField(max_length=300, null=True, blank=True)
    sign_date = models.DateField(null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    part_time = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, default=0)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    contract_subject = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    attachments = models.ManyToManyField(to=Attachment, through='EmployeeContractAttachment')

    def __str__(self):
        return self.code

    class Meta:
        db_table = 'employee_contract'


class EmployeeContractAttachment(models.Model):
    id_contract = models.ForeignKey(EmployeeContract, db_column='id_contract', on_delete=models.CASCADE)
    id_attachment = models.ForeignKey(Attachment, db_column='id_attachment', on_delete=models.CASCADE)
    sq = models.IntegerField()

    class Meta:
        db_table = 'employee_contract_attachment'


class Employee(models.Model):
    user = models.OneToOneField(User, primary_key=True, db_column='id', on_delete=models.CASCADE)
    document_type = models.ForeignKey(DocumentType, db_column='id_document_type', on_delete=models.CASCADE)
    hire_date = models.DateField(verbose_name=_('employee.hire_date'), null=True, blank=True)
    completion_date = models.DateField(verbose_name=_('employee.completion_date'), null=True, blank=True)
    init_holiday_days = models.IntegerField(verbose_name=_('employee.init_holiday_days'), default=0)
    curr_holiday_days = models.IntegerField(verbose_name=_('employee.curr_holiday_days'), default=0)
    prev_year_holiday_days = models.IntegerField(verbose_name=_('employee.prev_year_holiday_days'), default=0)
    curr_salary = models.DecimalField(verbose_name=_('employee.curr_salary'), max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return (self.user.first_name or '') + ' ' + (self.user.last_name or '')

    class Meta:
        db_table = 'user_employee'
