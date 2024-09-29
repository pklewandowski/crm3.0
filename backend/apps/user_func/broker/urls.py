from django.urls import re_path as url

from . import views
from .api import views as rest

urlpatterns = [
    url(r'^$', views.index, name='broker.index'),
    url(r'^list/$', views.ListView.as_view(), name='broker.list'),
    url(r'^list/(?P<process_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', views.ListView.as_view(), name='broker.list'),
    url(r'^add/(?P<id>\d+)/$', views.add, name='broker.add'),
    url(r'^get-brokers-for-adviser/$', rest.BrokersForAdviser.as_view(), name='broker.get_brokers_for_adviser'),
    # -------------------------------------- rest ------------------------------------------
    url(r'^csv/$', rest.BrokerCsv.as_view(), name='broker.csv'),
    url(r'^api/csv-import-template/$', rest.download, name='user.api.csv_import_template'),
    url(r'^get-list-for-select2/$', rest.get_list_for_select2, name='broker.get_list_for_select2'),
]
