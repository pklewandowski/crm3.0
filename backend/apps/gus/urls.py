from django.urls import re_path as url
from django.views.decorators.csrf import csrf_exempt

from .api import views as rest

urlpatterns = [
    # ---------------------- V2 -----------------
    url(r'^api/$', rest.GusManagerView.as_view(), name='gus.api'),
]
