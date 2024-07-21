from django.urls import re_path as url

from . import views

urlpatterns = [
    url(r'^close/$', views.Close.as_view(), name='notification.close'),
    # url(r'^add/(?P<type>\d+)/(?P<owner_id>\d+)/$', views.Add.as_view(), name='document.add'),
    ]