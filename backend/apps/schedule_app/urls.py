from django.urls import re_path as url

from apps.schedule_app import views

urlpatterns = [
    url(r'^$', views.index, name='schedule_app.index'),
]
