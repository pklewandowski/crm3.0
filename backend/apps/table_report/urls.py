from django.urls import re_path as url

from apps.table_report import views
from apps.table_report.api import views as rest

urlpatterns = [
    url(r'^$', views.report_list, name='table_report.list'),
    url(r'^(?P<code>\w+)/(?P<id>\d+)/$', views.TableReportView.as_view(), name='table_report.report'),
    url(r'^api/$', rest.TableReportWidget.as_view(), name='table_report.api'),
    url(r'^api/aggregate/$', rest.TableReportAggregateView.as_view(), name='table_report.api.aggregate')
]
