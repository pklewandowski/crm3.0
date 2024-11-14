from django.urls import re_path as url

from apps.product.api import views as rest
from apps.product.api.instalment_schedule import views as instalment_schedule_rest
from apps.product.view import commission_views
from apps.product.view import views

urlpatterns = [
    url(r'^$', views.index, name='attribute.index'),
    url(r'^list/(?P<id>\d+)/$', views.list_product, name='product.list'),
    url(r'^list-all/$', views.list_all_products, name='product.list_all_products'),
    url(r'^add/(?P<id>\d+)/$', views.add, name='product.add'),
    url(r'^add/(?P<id>\d+)/(?P<id_client>\d+)/$', views.add, name='product.add'),
    url(r'^edit/(?P<id>\d+)/$', views.edit, name='product.edit'),
    url(r'^edit/(?P<id>\d+)/(?P<iframe>\w+)/$', views.edit, name='product.edit'),
    url(r'^calculation-error/(?P<id>\d+)/(?P<iframe>\w+)/$', views.edit, name='product.calculation_error'),
    url(r'^day-calculation/$', views.day_calculation, name='product.day_calculation'),
    url(r'^type/list/$', views.list_product_type, name='product.type.list'),
    url(r'^type/interest/global/(?P<id>\d+)/$', views.interest_global, name='product.type.interest_global'),
    url(r'^action/add/(?P<id_product>\d+)/$', views.action_add, name='product.action.add'),
    url(r'^action/add/(?P<id_product>\d+)/(?P<id_action>\d+)/$', views.action_add, name='product.action.add'),
    url(r'^action/edit/(?P<id_product>\d+)/(?P<id_action>\d+)/$', views.action_edit, name='product.action.edit'),
    url(r'^action/action-delete/$', views.action_delete, name='product.action.delete'),
    url(r'^type/commission/add/(?P<id>\d+)/$', commission_views.add, name='product.type.commission.add'),
    url(r'^type/commission/edit/(?P<id>\d+)/$', commission_views.edit, name='product.type.commission.edit'),
    url(r'^type/commission/list/(?P<id>\d+)/$', commission_views.list, name='product.type.commission.list'),
    url(r'^temp-copy-paste/$', views.temp_copy_paste, name='product.temp_copy_paste'),

    url(r'^action-report-preview/$', views.action_report_preview, name='product.action.report.preview'),

    # ---------------------------------------- REST ----------------------------------------------
    url(r'^calc-table/$', rest.ProductCalcTable.as_view(), name='product.api.calc_table)'),
    url(r'^cash-flow/$', rest.ProductCashFlowApi.as_view(), name='product.api.cash_flow'),
    url(r'^cash-flow/aggregates/$', rest.ProductCashFlowAggregatesApi.as_view(),
        name='product.api.cash_flow_aggregates'),
    url(r'^api/$', rest.ProductApi.as_view(), name='product.api'),
    url(r'^global-interest/api/$', rest.ProductGlobalInterestView.as_view(), name='product.global_interest.api'),

    url(r'^cashflow/api/$', rest.ProductApi.as_view(), name='product.api'),
    url(r'^type/api/status$', rest.ProductTypeStatusApi.as_view(), name='product.type.api.status'),

    url(r'^api/instalment-schedule/$', instalment_schedule_rest.ProductInstalmentScheduleView.as_view(),
        name='product.api.instalment_schedule'),
    url(r'^api/instalment-schedule/mapping/$', instalment_schedule_rest.ProductInstalmentScheduleMappingView.as_view(),
        name='product.api.instalment_schedule.mapping'),

    url(r'^api/product-stats/$', rest.ProductStatView.as_view(), name='product.api.stats'),
    url(r'^api/balance-per-day/$', rest.ProductBalancePerDayView.as_view(), name='product.api.balance_per_day'),
]
