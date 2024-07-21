from django.urls import re_path as url
from apps.csv.api import views

urlpatterns = [
    url(r'^$', views.index, name='csv'),
    url(r'^process-csv/$', views.Csv.as_view(), name='csv.process_csv'),
]
