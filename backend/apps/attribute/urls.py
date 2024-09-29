from django.urls import re_path as url
from . import views
from .api import view as rest

urlpatterns = [
    # url(r'^$', views.index, name='attribute.index'),
    # url(r'^list/$', views.list, name='attribute.list'),
    # url(r'^add/$', views.add, name='attribute.add'),
    # url(r'^edit/(?P<id>\d+)/$', views.edit, name='attribute.edit'),
    url(r'^add/$', views.add, name='attribute.add'),
    url(r'^save-pasted-image/$', views.save_pasted_image, name='attribute.save_pasted_image'),
    url(r'^edit/(?P<id>\d+)/$', views.edit, name='attribute.edit'),
    url(r'^list/$', views.list, name='attribute.list'),
    # url(r'^object/add/(?P<id_object_type>\d+)/(?P<id>\d+)/$', views.add_attribute, name='attribute.object.add'),
    # url(r'^object/edit/(?P<id_object_type>\d+)/(?P<id>\d+)/$', views.edit_attribute, name='attribute.object.edit'),
    # url(r'^document/list/(?P<id_document_type>\d+)/(?P<id>\d+)/$', views.list_attribute, name='attribute.document.list'),

    # ------------------------------ REST --------------------------------------
    url(r'^api/$', rest.AttributeApi.as_view(), name='attribute.api'),
]
