from django.urls import re_path as url
from django.views.decorators.csrf import csrf_exempt

from .api import views as rest

urlpatterns = [
    # ---------------------- rest -----------------
    url(r'^api/history/$', rest.AddressHistoryApi.as_view(), name='address.history.api')
]
