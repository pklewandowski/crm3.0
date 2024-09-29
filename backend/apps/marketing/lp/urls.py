from django.urls import re_path as url
from . import views

urlpatterns = [
    url(r'^index/', views.index, name='marketing.lp.index'),
    url(r'^list/', views.List.as_view(), name='marketing.lp.list'),
    url(r'^medium/add', views.AddMedium.as_view(), name='marketing.lp.medium.add'),
    url(r'^medium/edit/(?P<id>\d+)/$', views.EditMedium.as_view(), name='marketing.lp.medium.edit'),
    url(r'^medium/list', views.ListMedium.as_view(), name='marketing.lp.medium.list'),
    url(r'^source/add', views.AddSource.as_view(), name='marketing.lp.source.add'),
    url(r'^source/edit/(?P<id>\d+)/$', views.EditSource.as_view(), name='marketing.lp.source.edit'),
    url(r'^source/list', views.ListSource.as_view(), name='marketing.lp.source.list'),
    url(r'^lead-page/add', views.AddLeadPage.as_view(),   name='marketing.lp.lead_page.add'),
    url(r'^lead-page/edit/(?P<id>\d+)/$', views.EditLeadPage.as_view(), name='marketing.lp.lead_page.edit'),
    url(r'^lead-page/list', views.ListLeadPage.as_view(), name='marketing.lp.lead_page.list'),
]
