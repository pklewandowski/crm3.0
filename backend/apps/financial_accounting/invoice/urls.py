from django.urls import re_path as url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='invoice.index'),
    url(r'^list/$', views.list, name='invoice.list'),
    url(r'^add/(?P<id>\d+)/$', views.add, name='invoice.add'),
    url(r'^edit/(?P<id>\d+)/$', views.edit, name='invoice.edit'),
]
