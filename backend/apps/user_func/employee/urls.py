from django.urls import re_path as url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='employee.index'),
    url(r'^list/', views.ListView.as_view(), name='employee.list'),
    url(r'^add/(?P<id>\d+)/$', views.add, name='employee.add'),
    url(r'^get-list-for-select2/$', views.get_list_for_select2, name='employee.get_list_for_select2'),
    url(r'^contract/list/(?P<id>\d+)/$', views.contract_list, name='employee.contract_list'),
    url(r'^contract/add/(?P<id_employee>\d+)/$', views.contract_add, name='employee.contract_add'),
    url(r'^contract/add/(?P<id_employee>\d+)/(?P<id_contract>\d+)/$', views.contract_add, name='employee.contract_add'),
    url(r'^contract-type/list/$', views.contract_type_list, name='employee.contract_type_list'),
    url(r'^contract-type/add/$', views.contract_type_add, name='employee.contract_type_add'),
    url(r'^contract-type/add/(?P<id>\d+)/$', views.contract_type_add, name='employee.contract_type_add'),

]
