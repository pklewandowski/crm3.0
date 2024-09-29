from django.urls import re_path as url

from . import views
from .api import views as rest

urlpatterns = [
    url(r'^$', views.TagListView.as_view(), name='tag.list'),
    url(r'^add/$', views.TagView.as_view(), name='tag.add'),
    url(r'^add/(?P<id>\d+)/$', views.TagView.as_view(), name='tag.edit'),
    # ------------------------------- REST ------------------------------------
    url(r'^api/$', rest.TagApi.as_view(), name='tag.api'),

]
