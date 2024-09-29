import traceback

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import py3ws
from apps.gus.gusapi import LitexClient


class GusManagerView(APIView):
    def get(self, request, *args, **kwargs):
        response_status = status.HTTP_200_OK

        try:
            nip = request.query_params.get('nip')
            py3ws.utils.validators.nip_validator(nip)
            gus = LitexClient()
            response_data = gus.get_by_nip(nip)

        except Exception as ex:
            response_data = {'errmsg': str(ex), 'traceback': traceback.format_exc()}
            response_status = status.HTTP_400_BAD_REQUEST

        return Response(data=response_data, status=response_status)
