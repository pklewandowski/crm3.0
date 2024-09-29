from django.urls import re_path as url
from . import views

urlpatterns = [

    url(r'^add/$', views.add, name='batch_processing.add'),
    url(r'^edit/(?P<id>\d+)/$', views.edit, name='batch_processing.edit'),
    url(r'^list/$', views.list, name='batch_processing.list'),

]
