import json

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render

from apps.document.forms import DocumentTypeForm
from apps.document.models import DocumentType, DocumentTypeAccounting, DocumentTypeAccountingType
from apps.document.type.forms import DocumentTypeActionFormset
from apps.document.utils import get_accounting_ordered_choosen_list, get_av_choosen_list
from apps.document.view_base import _save_document_type
from py3ws.auth.decorators.decorators import p3permission_required


@login_required()
@p3permission_required('documenttype.add_documenttype')
@transaction.atomic
def add_type(request):
    accounting_ordered_choosen_list = get_accounting_ordered_choosen_list(request.POST.get('accounting_ordered', None))
    form = DocumentTypeForm(request.POST or None)

    c = get_av_choosen_list(accounting_ordered_choosen_list)
    accounting_ordered_choosen = c['choosen']
    accounting_available = c['available']

    if request.method == 'POST':

        if form.is_valid():
            _save_document_type(form, accounting_ordered_choosen)
            return redirect('document.type.list')

    context = {'form': form, 'accounting_available': accounting_available, 'accounting_ordered_choosen': accounting_ordered_choosen}
    return render(request, 'document/type/add.html', context)


@login_required()
@p3permission_required('documenttype.change_documenttype')
@transaction.atomic
def edit_type(request, id):
    accounting_ordered_choosen_list = get_accounting_ordered_choosen_list(request.POST.get('accounting_ordered', None))
    document_type = DocumentType.objects.get(pk=id)

    if not document_type.editable:
        exclude_list = ('editable', 'code',)
    else:
        exclude_list = ()

    accounting_unordered_initial = [i.accounting_type
                                    for i in DocumentTypeAccounting.objects.filter(document_type=document_type,
                                                                                   accounting_type__is_accounting_order=False
                                                                                   )]

    form = DocumentTypeForm(data=request.POST or None,
                            exclude_list=exclude_list,
                            instance=document_type,
                            initial={
                                'accounting_unordered': accounting_unordered_initial,
                                'is_schedule': True,
                                'editable': True
                            })

    action_formset = DocumentTypeActionFormset(
        initial=document_type.financial_rules,
        data=request.POST or None,
        prefix='action_formset',
        form_kwargs={'document_type': document_type}
    )

    if request.method == 'POST':
        c = get_av_choosen_list(accounting_ordered_choosen_list)
        accounting_ordered_choosen = c['choosen']

        if form.is_valid() and action_formset.is_valid():
            document_type = _save_document_type(form, accounting_ordered_choosen)

            action_rules = sorted([i for i in action_formset.cleaned_data if not i.get('DELETE')], key=lambda k: int(k['sq']))
            document_type.financial_rules = action_rules

            document_type.save()

            return redirect('document.type.edit', document_type.pk)

    accounting_ordered_choosen = [i.accounting_type
                                  for i in DocumentTypeAccounting.objects.filter(accounting_type__is_accounting_order=True,
                                                                                 document_type=document_type).order_by('sq')]
    accounting_available = DocumentTypeAccountingType.objects.filter(is_accounting_order=True).exclude(pk__in=[i.pk for i in accounting_ordered_choosen])

    form.fields['accounting_unordered'].value = ['2']  # DocumentTypeAccounting.objects.filter(document_type=document_type, accounting_type__is_accounting_order=False).values(document_type.pk)

    context = {'document_type': document_type,#848493
               'form': form,
               'accounting_available': accounting_available,
               'accounting_ordered_choosen': accounting_ordered_choosen,
               'action_formset': action_formset
               }
    return render(request, 'document/type/add.html', context)
