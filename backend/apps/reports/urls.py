from django.urls import re_path as url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='meeting_room.index'),
    url(r'^list/$', views.list, name='report.list'),
    url(r'^add/$', views.meeting_room_attribute_add, name='meeting_room.attribute.add'),

]
