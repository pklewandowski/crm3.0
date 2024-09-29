from django.urls import re_path as url
from . import views


urlpatterns = [
    url(r'^$', views.index, name='meeting_room.index'),
    url(r'^list/$', views.meeting_room_list, name='meeting_room.list'),
    url(r'^attribute/list/$', views.meeting_room_attribute_list, name='meeting_room.attribute.list'),
    # url(r'^attribute/add/$', views.meeting_room_attribute_add, name='meeting_room.attribute.add'),
    # url(r'^attribute/add/(?P<id>\d+)/$', views.meeting_room_attribute_add, name='meeting_room.attribute.add'),
    url(r'^add/$', views.add, name='meeting_room.add'),
    url(r'^add/(?P<id>\d+)/$', views.add, name='meeting_room.add'),

]
