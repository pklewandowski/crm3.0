from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("Tu będzie funkcjonalność zarządzania logiem aplikacji.")
