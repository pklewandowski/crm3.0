from django.urls import re_path as url

from . import views

urlpatterns = [
    url(r'^add/$', views.Add.as_view(), name='partner.lead.add'),
    url(r'^list/$', views.List.as_view(), name='partner.lead.list'),
    url(r'^partner-status/$', views.Status.as_view(), name='partner.lead.status'),
    url(r'^add_broker/(?P<id>\d+)/$', views.AddBroker.as_view(), name='partner.lead.add.broker'),
    url(r'^add_client/(?P<id>\d+)/$', views.AddClient.as_view(), name='partner.lead.add.client'),
    url(r'^add_document/(?P<id>\d+)/$', views.AddDocument.as_view(), name='partner.lead.add.document'),
]
