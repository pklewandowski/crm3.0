import json

from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from py3ws.views.generic_view import GenericView

from apps.notification.utils import Notification
from apps.notification.views_base import NotificationView


class Close(NotificationView):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        status = 200
        response_data = {}
        id = request.POST.get('id')  # self.kwargs['id']
        try:
            with transaction.atomic():
                Notification.status(id=id, user=request.user, status='CL')
        except Exception as ex:
            response_data['errmsg'] = str(ex)
            status = 400
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=status)
