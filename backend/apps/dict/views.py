from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db import transaction
from django.db.models import Max
import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from py3ws.auth.decorators.decorators import p3permission_required

from apps.dict.models import Dictionary, DictionaryEntry


def index(request):
    return HttpResponse("dict.index")



# @p3permission_required('dict.list_dictionary')
def list(request):
    dictionary_list = Dictionary.objects.all()
    paginator = Paginator(dictionary_list, 10)
    page = request.GET.get('page')

    try:
        dictionaries = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        dictionaries = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        dictionaries = paginator.page(paginator.num_pages)

    context = {'dictionaries': dictionaries}
    return render(request, 'dict/list.html', context)



# @p3permission_required('dict.change_dictionary')
def edit(request):
    return HttpResponse("dict.edit")




def entry_list_edit(request, id):
    dict = get_object_or_404(Dictionary, pk=id)
    entries = DictionaryEntry.objects.filter(dictionary=dict).order_by('sq')

    context = {'dict': dict, 'entries': entries}
    return render(request, 'dict/entry/list_edit.html', context)


def entry_list_view(request, id):
    dict = get_object_or_404(Dictionary, pk=id)
    entries = DictionaryEntry.objects.filter(dictionary=dict).order_by('sq')

    context = {'dict': dict, 'entries': entries}
    return render(request, 'dict/entry/list_view.html', context)



# @p3permission_required('dict.add_dictionaryentry')
@transaction.atomic()
def entry_add(request):
    try:
        response_data = {}

        value = request.POST.get('entry[value]')
        label = request.POST.get('entry[label]')
        id_dict = request.POST.get('entry[id_dict]')

        if label is None:
            raise Exception('[entry_add]: Brak parametru [LABEL]')
        if id_dict is None:
            raise Exception('[entry_add]: Brak parametru [ID_DICT]')

        dictionary = get_object_or_404(Dictionary, pk=int(id_dict))

        entry = DictionaryEntry()
        entry.value = value or None
        entry.label = label
        entry.active = True
        entry.dictionary = dictionary

        sq = DictionaryEntry.objects.filter(dictionary=dictionary).aggregate(Max('sq'))['sq__max'] or 0

        entry.sq = sq + 1

        entry.save()

        response_data['status'] = 'OK'

    except Exception as e:
        response_data['status'] = 'ERROR'
        response_data['message'] = str(e)

    return HttpResponse(json.dumps(response_data), content_type="application/json")



# @p3permission_required('dict.change_dictionaryentry')
@transaction.atomic()
def entry_edit(request):
    response_data = {}
    try:
        id = request.POST.get('entry[id]')
        value = request.POST.get('entry[value]')
        label = request.POST.get('entry[label]')

        entry = get_object_or_404(DictionaryEntry, pk=id)

        if not entry.dictionary.editable:
            raise Exception('Słownik nie jest edytowalny')

        entry.value = value
        entry.label = label
        entry.save()

        response_data['status'] = 'OK'

    except Exception as e:
        response_data['status'] = 'ERROR'
        response_data['message'] = str(e)

    return HttpResponse(json.dumps(response_data), content_type="application/json")



# @p3permission_required('dict.activate_dictionaryentry', 'Brak uprawnień do zmiany aktywności wpisu')
@transaction.atomic()
def entry_active(request):
    try:
        response_data = {}
        id = request.POST.get('entry[id]')
        active = request.POST.get('entry[active]')

        if id is None:
            raise Exception('[entry_active]: Brak parametru [ID] dla wpisu słownika')
        if active is None:
            raise Exception('[entry_active]: Brak parametru [ACTIVE] dla wpisu słownika')

        de = get_object_or_404(DictionaryEntry, pk=id)
        de.active = active
        de.save()

        response_data['status'] = 'OK'

    except Exception as e:
        response_data['status'] = 'ERROR'
        response_data['message'] = str(e)

    return HttpResponse(json.dumps(response_data), content_type="application/json")



