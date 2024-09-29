from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db import transaction
from django.conf import settings
from django.core.serializers import serialize
from django.views.decorators.csrf import csrf_exempt

from apps.product.forms import ProductCommissionTypeForm


def add(request):
    form = ProductCommissionTypeForm(request.POST or None)

    if form.is_valid():
        pass
    context = {'form': form}

    return render(request, 'product/commission/type/add.html', context=context)
