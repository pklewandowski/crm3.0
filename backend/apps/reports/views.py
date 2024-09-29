from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext as _
from django.db import transaction
from django.contrib import messages
from django.http import HttpResponse, JsonResponse


def index(request):
    return HttpResponse(_("reports index"))


def list(request):
    context = {}
    return render(request, 'reports/list.html', context)


def add(request):
    return HttpResponse(_("report add"))


