import traceback

from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status as http_status

from apps.user_func.adviser.models import Adviser


@api_view(['GET'])
def get_list_for_select_2(request):
    key = request.query_params.get('q', None)
    id = request.query_params.get('id', None)
    exclude = request.query_params.get('exclude', None)

    response_data = {}
    response_status = http_status.HTTP_200_OK

    q = Q(pk=id) if id else Q(user__is_active=True) & (
            Q(user__last_name__icontains=key) |
            Q(user__first_name__icontains=key) |
            Q(user__phone_one__icontains=key)
    ) if key else None

    if q and exclude:
        q = q.exclude(pk__in=exclude)

    try:
        result = Adviser.objects.filter(q)
        response_data['results'] = [{'id': i.pk, 'text': (i.user.first_name + ' ' if i.user.first_name else '') + (i.user.last_name or '')} for i in result]

    except Exception as e:
        response_status = http_status.HTTP_400_BAD_REQUEST
        response_data['errmsg'] = str(e)
        response_data['traceback'] = traceback.format_exc()

    return Response(response_data, status=response_status)
