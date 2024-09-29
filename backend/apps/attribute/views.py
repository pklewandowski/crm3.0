from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db import transaction
from .models import Attribute
from .forms import AttributeForm
from py3ws.forms import utils as form_utils
import pprint
from django.views.decorators.csrf import csrf_exempt
import json
import uuid


def index(request):
    return HttpResponse("agreement")


@transaction.atomic
def add(request):
    form = AttributeForm(request.POST or None)
    form.fields['generic_datatype'].choices = form_utils.get_dictionary_entries('GENERIC_DATATYPES')

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('attribute.list')

    context = {'form': form}
    return render(request, 'attribute/datatype/add.html', context)


@transaction.atomic
def edit(request, id):
    datatype = get_object_or_404(Attribute, pk=id)
    form = AttributeForm(request.POST or None, instance=datatype)
    form.fields['generic_datatype'].choices = form_utils.get_dictionary_entries('GENERIC_DATATYPES')

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('attribute.list')
    context = {'form': form}
    return render(request, 'attribute/datatype/add.html', context)


def list(request):
    datatypes = Attribute.objects.all()
    context = {'datatypes': datatypes}
    return render(request, 'attribute/datatype/list.html', context)


@csrf_exempt
def save_pasted_image(request):
    fname = uuid.uuid4().hex
    with open('media/tmp/%s' % fname, 'wb+') as destination:
        for chunk in request.FILES['blob'].chunks():
            destination.write(chunk)
    return HttpResponse(json.dumps({'name':fname}), content_type="application/json")
