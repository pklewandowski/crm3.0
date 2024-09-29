from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView


def index(request):
    return HttpResponse('csv')


class Csv(APIView):
    def get(self, request):
        return Response([{'ala': 'makota'}])

    def post(self, request):
        return Response(data=[{"col1": "value1_1", "col2": "value1_2"}, {"col1": "value2_1", "col2": "value2_2"}])
