from django.urls import re_path as url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='ocr.index'),
    url(r'^ocr/$', views.ocr, name='ocr.ocr'),
]

