import json
import traceback

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, F
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from py3ws.views import generic_view

from apps.user.models import User
from apps.user_func import utils

from .forms import EmployeeContractTypeForm, EmployeeContractForm
from .models import Employee, EmployeeContractType, EmployeeContract
from . import USER_TYPE_CODE


def index(request):
    return HttpResponse("Zarządzanie funkcjonalnościami pracowników.")


class ListView(generic_view.ListView):
    def set_mode(self):
        self._mode = settings.MODE_VIEW

    def set_app_name(self):
        self._app_name = 'user_func.employee'

    def __init__(self):
        self.default_sort_field = 'user__last_name'
        self.document_code = USER_TYPE_CODE
        super(ListView, self).__init__()

    def set_where(self):
        self.where = Q(user__is_active=True)
        if self.search:
            self.where &= (Q(user__first_name__icontains=self.search) |
                           Q(user__last_name__icontains=self.search) |
                           Q(user__phone_one__icontains=self.search) |
                           Q(user__email__icontains=self.search)
                           )

    def set_query(self):
        self.query = Employee.objects.filter(self.where).select_related('user'). \
            annotate(first_name=F('user__first_name'),
                     last_name=F('user__last_name'),
                     email=F('user__email'),
                     phone_one=F('user__phone_one'),
                     date_joined=F('user__date_joined')
                     ).order_by('%s%s' % (self.sort_dir, self.sort_field))

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        super(ListView, self).dispatch(request, *args, **kwargs)
        return self.list(request=request, template='user/_list.html')


@transaction.atomic()
def add(request, id):
    return utils.add('apps.user_func.employee.models.Employee', id, USER_TYPE_CODE)


def contract_type_list(request):
    contract_types = EmployeeContractType.objects.all()
    context = {'contract_types': contract_types}
    return render(request, 'employee/contract_type/list.html', context)


def contract_type_add(request, id=None):
    try:
        form = None
        if id is not None:
            contract_type = get_object_or_404(EmployeeContractType, pk=id)
        else:
            contract_type = None

        form = EmployeeContractTypeForm(request.POST or None, instance=contract_type, label_suffix=':',
                                        prefix='contract_type')
        if request.method == 'POST':
            form.save()
            return redirect('employee.contract_type_list')

    except Exception as e:
        messages.add_message(request, messages.ERROR, e)

    context = {'form': form}
    return render(request, 'employee/contract_type/add.html', context)


def contract_list(request, id):
    employee = get_object_or_404(Employee, pk=id)
    user = get_object_or_404(User, pk=id)
    contracts = EmployeeContract.objects.filter(employee=employee)
    context = {'contracts': contracts, 'employee': employee, 'user': user}
    return render(request, 'employee/contract/list.html', context)


def contract_add(request, id_employee, id_contract=None):
    try:
        form = None
        employee = get_object_or_404(Employee, pk=id_employee)
        if id_contract is not None:
            contract = get_object_or_404(EmployeeContract, pk=id_contract)
        else:
            contract = None

        form = EmployeeContractForm(request.POST or None, instance=contract, label_suffix=':', prefix='contract')

        if request.method == 'POST':
            contract = form.save(commit=False)
            contract.employee = employee
            contract.save()
            return redirect('employee.contract_list', id=employee.pk)

    except Exception as e:
        messages.add_message(request, messages.ERROR, e)

    context = {'form': form}
    return render(request, 'employee/contract/add.html', context)


@login_required()
@csrf_exempt
def get_list_for_select2(request):
    key = request.GET.get('q', None)
    employee_id = request.GET.get('id', None)
    response_data = {}
    response_status = status.HTTP_200_OK

    q = Q(pk=employee_id) if employee_id else Q(user__first_name__icontains=key) | Q(user__last_name__icontains=key) | Q(user__phone_one__icontains=key)

    try:
        response_data['results'] = [{'id': i.pk, 'text': str(i.user)} for i in Employee.objects.filter(q)]

    except Exception as e:
        response_status = status.HTTP_400_BAD_REQUEST
        response_data = {'errmsg': str(e), "traceback": traceback.format_exc()}

    return HttpResponse(json.dumps(response_data), content_type="application/json", status=response_status)
