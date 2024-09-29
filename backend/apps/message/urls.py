from django.urls import re_path as url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='message.index'),
    url(r'^send/$', views.send, name='message.send'),
    url(r'^queue_list/$', views.ListView.as_view(), name='message.template.queue_list'),
    url(r'^queue-preview/$', views.queue_preview, name='message.queue_preview'),
    url(r'^test-message/$', views.test_message, name='message.test_message'),
    url(r'^template/add/$', views.Add.as_view(), name='message.template.add'),
    url(r'^template/edit/(?P<id>\d+)/$', views.Edit.as_view(), name='message.template.edit'),
    url(r'^template/list/$', views.list_template, name='message.template.list'),
]
