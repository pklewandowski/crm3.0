from django.conf import settings
from django.db.models import Sum, F
from django.db.models.functions import Coalesce
from django.forms import modelformset_factory
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.db import transaction

import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from apps.document.forms import DocumentForm
from apps.document import utils as doc_utils
from apps.document.models import Document, DocumentType
from apps.financial_accounting.invoice.models import InvoiceItem, Invoice, InvoiceExtraItem
from apps.hierarchy.models import Hierarchy
from .forms import InvoiceForm, InvoiceItemForm, InvoiceExtraItemForm
from py3ws.auth.decorators.decorators import p3permission_required
import pprint


def index(request):
    return HttpResponse("dict.index")


def list(request):
    document_type = DocumentType.objects.get(pk=21)
    invoices = Invoice.objects.all().annotate(
        total=Coalesce(Sum((F('item_set__unit_price') * F('item_set__quantity')) +
                           (F('item_set__unit_price') * F('item_set__quantity')) * (F('item_set__tax_value') / 100)), 0),
        total_extra=Coalesce(Sum('extra_item_set__value'), 0)
    )
    context = {'invoices': invoices, 'document_type': document_type}
    return render(request, 'invoice/list.html', context=context)


@transaction.atomic()
def add(request, id):
    document = Document.objects.get(pk=id)
    hierarchy = Hierarchy.objects.get(level=0, id=1).get_descendants()

    InvoiceItemFormset = modelformset_factory(InvoiceItemForm.Meta.model, form=InvoiceItemForm, extra=0, can_delete=True)
    InvoiceExtraItemFormset = modelformset_factory(InvoiceExtraItemForm.Meta.model, form=InvoiceExtraItemForm, extra=0, can_delete=True)

    form = InvoiceForm(request.POST or None)
    document_form = DocumentForm(data=request.POST or None, instance=document, prefix='document')
    invoice_item_formset = InvoiceItemFormset(data=request.POST or None, prefix='invoiceitem', queryset=InvoiceItem.objects.none())
    invoice_extra_item_formset = InvoiceExtraItemFormset(data=request.POST or None, prefix='invoiceextraitem', queryset=InvoiceExtraItem.objects.none())

    # for i in invoice_item_formset:
    #     i.fields['invoice'].required = False
    #
    # for i in invoice_extra_item_formset:
    #     i.fields['invoice'].required = False

    if request.POST:

        if all([form.is_valid(),
                document_form.is_valid(),
                invoice_item_formset.is_valid(),
                invoice_extra_item_formset.is_valid()]):

            document = document_form.save(commit=False)
            document.status = doc_utils.get_initial_status(type=document.type).code
            document.hierarchy = Hierarchy.objects.get(pk=13)
            document.save()
            invoice = form.save(commit=False)
            invoice.document = document
            invoice.save()

            item = invoice_item_formset.save(commit=False)
            for i in item:
                i.invoice = invoice
                i.save()
            item = invoice_extra_item_formset.save(commit=False)
            for i in item:
                i.invoice = invoice
                i.save()

            return redirect('invoice.edit', invoice.pk)

    context = {
        'hierarchy': hierarchy,
        'document': document,
        'form': form,
        'document_form': document_form,
        'invoice_item_formset': invoice_item_formset,
        'invoice_extra_item_formset': invoice_extra_item_formset,
        'mode': settings.MODE_CREATE
    }

    return render(request, 'invoice/add.html', context)


@transaction.atomic()
def edit(request, id):
    invoice = Invoice.objects.get(pk=id)
    document = invoice.document
    hierarchy = Hierarchy.objects.get(level=0, id=1).get_descendants()

    InvoiceItemFormset = modelformset_factory(InvoiceItemForm.Meta.model,
                                              form=InvoiceItemForm, extra=0, can_delete=True)
    InvoiceExtraItemFormset = modelformset_factory(InvoiceExtraItemForm.Meta.model, form=InvoiceExtraItemForm, extra=0, can_delete=True)

    form = InvoiceForm(request.POST or None, instance=invoice)
    document_form = DocumentForm(request.POST or None, instance=document, prefix='document')
    document_form.fields['status_flow'].choices = [(None, '-----')] + [(i.available_status.code, i.available_status.name)
                                                                       for i in doc_utils.get_available_statuses(type=document.type, code=document.status)]
    invoice_item_formset = InvoiceItemFormset(data=request.POST or None, prefix='invoiceitem', queryset=invoice.item_set.all())
    invoice_extra_item_formset = InvoiceExtraItemFormset(data=request.POST or None, prefix='invoiceextraitem', queryset=invoice.extra_item_set.all())

    if request.POST:

        if all([
            form.is_valid(),
            document_form.is_valid(),
            invoice_item_formset.is_valid(),
            invoice_extra_item_formset.is_valid()
        ]):
            document = document_form.save(commit=False)
            if document_form.cleaned_data.get('status_flow'):
                document.status = document_form.cleaned_data.get('status_flow')
            document.save()
            form.save()
            invoice_item_formset.save()
            invoice_extra_item_formset.save()

            return redirect('invoice.list')

    context = {
        'hierarchy': hierarchy,
        'document': document,
        'form': form,
        'document_form': document_form,
        'invoice_item_formset': invoice_item_formset,
        'invoice_extra_item_formset': invoice_extra_item_formset,
        'mode': settings.MODE_EDIT
    }

    return render(request, 'invoice/edit.html', context)
