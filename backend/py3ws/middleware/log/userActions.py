import datetime
import json

from django.urls import resolve
from django.utils.deprecation import MiddlewareMixin

from apps.log.models import LogUserAction


# TODO: Stworzyć logera jako reusable app

class UserActionLogger(MiddlewareMixin):
    def process_request(self, request):
        if request.POST:
            action_type = 'SUBMIT'
        else:
            action_type = 'VIEW'
        LogUserAction.objects.create(username=request.user.username,
                                     user_id=request.user.id,
                                     request_path=request.path_info or '',
                                     url_name=resolve(request.path_info).url_name or '',
                                     parameter_list=json.dumps(resolve(request.path_info).kwargs) or '{}',
                                     action_type=action_type,
                                     date_created=datetime.datetime.now())
