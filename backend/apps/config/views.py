from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import FormAttribute


def index(request):
    return render(request, 'config/index.html', {})
