from django.urls import re_path as url

from apps.file_repository.api import views as rest
from . import views

urlpatterns = [
    url(r'^$', views.FileRepositoryListView.as_view(), name='tag.list'),
    url(r'^get-file/$', views.get_file, name='file.repository.get_file'),
    url(r'^get-file/(?P<id>\d+)/$', views.get_file, name='file.repository.get_file'),
    # ---------------------------- REST ---------------------------------------
    url(r'^api/$', rest.FileRepositoryView.as_view(), name='file.repository.api')
]