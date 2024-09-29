from django.urls import re_path as url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='transaction.index'),
    # url(r'^add/$', views.add, name='transaction.add'),
    # url(r'^add/(?P<id>\d+)/$', views.add, name='transaction.add'),

]
