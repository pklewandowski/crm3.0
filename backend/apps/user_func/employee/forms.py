from django.utils.translation import gettext_lazy as _
from django import forms
from django.forms import ModelForm
from .models import Employee, EmployeeContract, EmployeeContractType
from py3ws.forms import p3form

class EmployeeForm(p3form.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)


    class Meta:
        model = Employee
        fields = ['hire_date', 'completion_date', 'init_holiday_days', 'curr_holiday_days',
                  'prev_year_holiday_days', 'curr_salary', ]
        labels = {
            "hire_date": _("employee.form.label.hire_date"),
            "completion_date": _("employee.form.label.completion_date"),
            "init_holiday_days": _("employee.form.label.init_holiday_days"),
            "curr_holiday_days": _("employee.form.label.curr_holiday_days"),
            "prev_year_holiday_days": _("employee.form.label.prev_year_holiday_days"),
            "curr_salary": _("employee.form.label.curr_salary"),
        }


class EmployeeContractTypeForm(p3form.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EmployeeContractTypeForm, self).__init__(*args, **kwargs)

    class Meta:
        model = EmployeeContractType
        fields = ['code', 'name', 'part_time', 'description']
        labels = {
            "code": _("employee_contract_type.form.label.code"),
            "name": _("employee_contract_type.form.label.name"),
            "part_time": _("employee_contract_type.form.label.part_time"),
            "description": _("employee_contract_type.form.label.description"),
        }


class EmployeeContractForm(p3form.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EmployeeContractForm, self).__init__(*args, **kwargs)

    class Meta:
        model = EmployeeContract
        fields = ['type', 'code', 'salary', 'contract_subject', 'sign_date', 'start_date', 'end_date', 'part_time',
                  'description']
        labels = {
            "type": _("employee_contract.form.label.type"),
            "code": _("employee_contract.form.label.code"),
            "salary": _("employee_contract.form.label.salary"),
            "sign_date": _("employee_contract.form.label.sign_date"),
            "start_date": _("employee_contract.form.label.start_date"),
            "end_date": _("employee_contract.form.label.end_date"),
            "part_time": _("employee_contract.form.label.part_time"),
            "contract_subject": _("employee_contract.form.label.contract_subject"),
            "description": _("employee_contract.form.label.description"),
        }