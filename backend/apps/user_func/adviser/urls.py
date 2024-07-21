from django.urls import re_path as url

from . import views
from .api import views as rest
urlpatterns = [
    url(r'^$', views.index, name='adviser.index'),
    url(r'^list/$', views.ListView.as_view(), name='adviser.list'),
    url(r'^add/(?P<id>\d+)/$', views.add, name='adviser.add'),
    # ---------------------------------------------- rest ----------------------------------------------
    url(r'^get-list-for-select2/$', rest.get_list_for_select_2, name='adviser.get_list_for_select2'),
]
