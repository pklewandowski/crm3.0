from django.urls import re_path as url

from apps.report import views_v2
from . import views
from .api import views as rest

urlpatterns = [
    # url(r'^$', views.index, name='report.index'),
    # url(r'^list/$', views.list, name='report.list'),
    url(r'^add/(?P<template_id>\d+)/(?P<document_id>\d+)/$', views_v2.add, name='report.add'),
    # url(r'^download/(?P<id>\d+)/$', views.download, name='report.download'),
    url(r'^download/(?P<id>\d+)/$', views_v2.download, name='report.download'),

    #     API
    url(r'^api/$', rest.ReportApi.as_view(), name='report.api'),
    url(r'^api/template/$', rest.ReportTemplateApi.as_view(), name='report_template.api'),

]
