from django.urls import re_path as url

from . import views
from .api import views as rest

urlpatterns = [
    url(r'^$', views.index, name='hierarchy.index'),
    url(r'^list/$', views.list, name='hierarchy.list'),
    url(r'^user-list/$', views.user_list, name='hierarchy.user_list'),
    url(r'^delete/$', views.delete, name='hierarchy.delete'),

    url(r'^api/$', rest.HierarchyApi.as_view(), name='hierarchy.api'),
    url(r'^api/groups/$', rest.HierarchyApi.as_view(), name='hierarchy.api.groups'),
    url(r'^api/group/get-for-select2/$', rest.HierarchyApi.as_view(), name='hierarchy.api.group.get_for_select2'),
    url(r'^api/move/$', rest.HierarchyApi.as_view(), name='hierarchy.api.move'),

    url(r'^get-subcompany-for-select/$', rest.get_company_list_for_select, name='hierarchy.get_subcompany_for_select'),
]
