from django.urls import re_path as url

from . import views
from .api import views as rest
from .views import CurrentContactsView

urlpatterns = [
    url(r'^$', views.index, name='client.index'),
    url(r'^list/$', views.List.as_view(), name='client.list'),
    url(r'^list/(?P<process_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', views.List.as_view(), name='client.list'),
    url(r'^get-list/$', views.get_list, name='client.get_list'),
    url(r'^get-list-for-select2/$', views.get_list_for_select2, name='client.get_list_for_select2'),
    # url(r'^edit/(?P<id>\d+)/$', views.edit, name='client.edit'),
    url(r'^add/(?P<id>\d+)/$', views.add, name='client.add'),
    url(r'^complete/(?P<token>[a-zA-Z0-9-]+)/$', views.complete, name='client.complete'),
    url(r'^get-clients-for-adviser-select2/$', views.get_clients_for_adviser_select2, name='adviser.get_clients_for_adviser_select2'),
    url(r'^current-contacts/$', CurrentContactsView.as_view(), name='client.current_contacts'),
    # ------------------------------------   REST  ----------------------------------------------
    url(r'^csv/$', rest.ClientCsv.as_view(), name='client.csv'),
    url(r'^api/csv-import-template/$', rest.download, name='user.api.csv_import_template'),
]
