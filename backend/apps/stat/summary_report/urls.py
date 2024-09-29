from django.urls import re_path as url

from . import views

urlpatterns = [
    url(r'^$', views.Index.as_view(), name='stat.index'),
    url(r'^get-data/$', views.get_data, name='stat.get_data'),
    url(r'^get-pivot-data/$', views.get_pivot_data, name='stat.get_pivot_data'),
    url(r'^get-adviser-rank-data/$', views.get_adviser_rank_data, name='stat.get_adviser_rank_data'),

    url(r'^group/adviser/add/$', views.AddGroupAdviser.as_view(), name='stat.add_group_adviser'),
    url(r'^group/adviser/edit/(?P<id>\d+)/$', views.EditGroupAdviser.as_view(), name='stat.edit_group_adviser'),
    url(r'^group/adviser/delete/$', views.DeleteGroupAdviser.as_view(), name='stat.delete_group_adviser'),

    url(r'^group/loan-status/add/$', views.AddGroupLoanStatus.as_view(), name='stat.add_group_loan_status'),
    url(r'^group/loan-status/edit/(?P<id>\d+)/$', views.EditGroupLoanStatus.as_view(), name='stat.edit_group_loan_status'),
    url(r'^group/loan-status/delete/$', views.DeleteGroupLoanStatus.as_view(), name='stat.delete_group_loan_status'),
]
