import traceback

from rest_framework import status as http_status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.address.api.serializers import AddressSerializer, AddressHistorySerializer
from apps.address.models import Address


class AddressException(Exception):
    pass


class AddressApi(APIView):
    pass


class AddressHistoryApi(APIView):

    def get(self, request):
        response_status = http_status.HTTP_200_OK
        response_data = []
        address_id = request.query_params.get('addressId', None)
        try:
            if not address_id:
                raise AddressException('Podmiot nie posiada historii adresu wybranego typu.')

            address = Address.objects.get(pk=request.query_params.get('addressId'))
            response_data = AddressHistorySerializer(address.history.all().order_by('-history_date'), many=True).data

        except Exception as ex:
            response_data = {'errmsg': str(ex), 'traceback': traceback.format_exc()}
            response_status = http_status.HTTP_400_BAD_REQUEST

        return Response(data=response_data, status=response_status)
