from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db import transaction
from django.conf import settings
from django.core.serializers import serialize
from django.views.decorators.csrf import csrf_exempt

from apps.product.forms import ProductTypeCommissionForm
from apps.product.models import ProductTypeCommission
from apps.document.models import DocumentType


def list(request, id):
    document_type = DocumentType.objects.get(pk=id)
    commission_list = ProductTypeCommission.objects.filter(document_type=DocumentType.objects.get(pk=id))
    context = {'commission_list': commission_list, 'document_type': document_type}
    return render(request, 'product/commission/type/list.html', context=context)


@transaction.atomic()
def add(request, id):
    document_type = DocumentType.objects.get(pk=id)
    form = ProductTypeCommissionForm(request.POST or None)

    if form.is_valid():
        commission_type = form.save(commit=False)
        commission_type.document_type = document_type
        commission_type.save()
        return redirect('product.type.commission.list', id=document_type.pk)

    context = {'form': form, 'document_type': document_type}

    return render(request, 'product/commission/type/add.html', context=context)


@transaction.atomic()
def edit(request, id):
    commission = ProductTypeCommission.objects.get(pk=id)
    form = ProductTypeCommissionForm(request.POST or None, instance=commission)

    if form.is_valid():
        form.save()
        return redirect('product.type.commission.list', id=commission.document_type.pk)

    context = {'form': form}

    return render(request, 'product/commission/type/edit.html', context=context)
