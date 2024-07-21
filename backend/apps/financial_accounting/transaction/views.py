from django.forms import modelformset_factory
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db import transaction

import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def index(request):
    return HttpResponse("transaction.index")

