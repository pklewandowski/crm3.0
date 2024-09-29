from django.urls import re_path as url
from django.views.decorators.csrf import csrf_exempt
from . import views

urlpatterns = [
    url(r'^$', views.index, name='config'),
]
