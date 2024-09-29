from django.urls import re_path as url
from . import views
from .api import view as rest

urlpatterns = [
    # url(r'^$', views.index, name='attachment.index'),
    url(r'^get-tree/$', views.get_tree, name='attachment.get_tree'),
    url(r'^upload/$', views.upload, name='attachment.upload'),
    url(r'^basic/file-upload/$', views.basic_file_upload, name='attachment.basic_file_upload'),
    url(r'^basic/scan-upload/$', views.basic_scan_upload, name='attachment.basic_scan_upload'),
    url(r'^basic/prtscn-upload/$', views.basic_prtscn_upload, name='attachment.basic_prtscn_upload'),
    url(r'^download/(?P<id>\d+)/$', views.download, name='attachment.download'),
    url(r'^download_file/(?P<file_name>[.\w]+)/$', views.download_file, name='attachment.download_file'),
    url(r'^move/$', views.move, name='attachment.move'),
    url(r'^remove/$', views.remove, name='attachment.remove'),
    url(r'^add-directory/$', views.add_directory, name='attachment.add_directory'),
    url(r'^delete-directory/$', views.delete_directory, name='attachment.delete_directory'),
    url(r'^details/$', views.details, name='attachment.details'),
    url(r'^get-zip-attachments/(?P<id>\d+)/$', views.get_zip_attachemnts, name='attachment.get_zip_attachemnts'),
    #     REST
    url(r'^api/tree/$', rest.TreeApi.as_view(), name='attachment.tree')
]
