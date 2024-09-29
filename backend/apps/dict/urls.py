from django.urls import re_path as url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='dict.index'),
    url(r'^list/$', views.list, name='dict.list'),
    url(r'^dict-edit/$', views.list, name='dict.edit'),
    url(r'^entry/list/edit/(?P<id>\d+)/$', views.entry_list_edit, name='dict.entry_list_edit'),
    url(r'^entry/list/view/(?P<id>\d+)/$', views.entry_list_view, name='dict.entry_list_view'),
    url(r'^entry/entry-add/$', views.entry_add, name='dict.entry_add'),
    url(r'^entry/entry-edit/$', views.entry_edit, name='dict.entry_edit'),
    url(r'^entry/entry-active/$', views.entry_active, name='dict.entry_active'),
]
