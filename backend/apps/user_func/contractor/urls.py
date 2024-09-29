from django.urls import re_path as url

from . import views
from .api import views as rest

urlpatterns = [
    url(r'^$', views.index, name='contractor.index'),
    url(r'^list/$', views.List.as_view(), name='contractor.list'),
    url(r'^get-list/$', views.get_list, name='contractor.get_list'),
    url(r'^get-list-for-select2/$', views.get_list_for_select2, name='contractor.get_list_for_select2'),
    # url(r'^edit/(?P<id>\d+)/$', views.edit, name='client.edit'),
    url(r'^add/(?P<id>\d+)/$', views.add, name='contractor.add'),

    # ----------------------------------rest
    url(r'^api/$', rest.ContractorApi.as_view(), name='contractor.api')

]
