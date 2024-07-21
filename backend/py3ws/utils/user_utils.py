from django.http import HttpResponse, JsonResponse
import json
from .utils import get_class
from django.db.models import Q


# def user_autocomplete_list(request, class_name):
#     response_data = {'data': None, 'message': None}
#     try:
#         ids = json.loads(request.POST.get('id'))
#         key = request.POST.get('key')
#
#         if len(key) > 0:
#             data = get_class(class_name).objects.filter(Q(user__first_name__icontains=key) |
#                                             Q(user__last_name__icontains=key) |
#                                             Q(user__personal_id__icontains=key) |
#                                             Q(user__nip__icontains=key)).exclude(pk__in=ids).values('pk',
#                                                                                                     'user__first_name',
#                                                                                                     'user__last_name',
#                                                                                                     'user__email',
#                                                                                                     'user__personal_id',
#                                                                                                     'user__nip')
#             if data:
#                 c_list = []
#                 for c in data:
#                     c_list.append(
#                         {'pk': c['pk'],
#                          'first_name': c['user__first_name'],
#                          'last_name': c['user__last_name'],
#                          'email': c['user__email'],
#                          'personal_id': c['user__personal_id'],
#                          'nip': c['user__nip']})
#
#                 response_data['data'] = c_list  # serializers.serialize("json", clients, fields=('pk', 'user__first_name', 'user__last_name'))
#
#         response_data['status'] = 'OK'
#
#     except Exception as e:
#         response_data['status'] = 'ERROR'
#         response_data['message'] = str(e)
#
#     return HttpResponse(json.dumps(response_data), content_type="application/json")