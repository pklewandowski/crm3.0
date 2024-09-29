from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Zarządzanie skanowaniem.")


def ocr(request):
    return render(request, 'ocr/ocr.html')
