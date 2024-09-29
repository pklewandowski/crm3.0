from django.urls import re_path as url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='agreement.index'),
    url(r'^list/$', views.list, name='agreement.list'),
    url(r'^add/$', views.add, name='agreement.add'),
    url(r'^edit/(?P<id>\d+)/$', views.edit, name='agreement.edit'),
]

