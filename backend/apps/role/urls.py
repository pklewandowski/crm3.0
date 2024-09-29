from django.urls import re_path as url
from . import views

#app_name = 'role'
urlpatterns = [
    url(r'^$', views.index, name='role.index'),
    url(r'^list/$', views.role_list, name='role.list'),
    url(r'^user-list/$', views.role_user_list, name='role.user_list'),
    url(r'^delete/$', views.role_delete, name='role.delete'),
]
