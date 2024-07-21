import traceback

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.attribute.api.serializers import AttributeSerializer
from apps.attribute.api.services import services


class AttributeApi(APIView):
    def get(self, request):
        response_status = status.HTTP_200_OK
        action = request.query_params.get('action')
        response_data = {}
        try:
            if action == '__GET_LIST__':
                response_data = AttributeSerializer(services.get_list(), many=True).data
        except Exception as ex:
            response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
            response_data = {"errmsg": str(ex), "traceback": traceback.format_exc()}

        return Response(data=response_data, status=response_status)
