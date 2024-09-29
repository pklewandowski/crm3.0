import traceback

from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.user_func.contractor.api.serializers import ContractorSerializer
from apps.user_func.contractor.models import Contractor


class ContractorApi(APIView):
    def get(self, request):
        response_status = status.HTTP_200_OK
        response_data = {}
        try:
            contractor_serializer = ContractorSerializer(Contractor.objects.get(pk=request.query_params.get('contractorId')))
            response_data = contractor_serializer.data

        except Exception as ex:
            response_data['errmsg'] = str(ex)
            response_data['traceback'] = traceback.format_exc()
        return Response(data=response_data, status=response_status)
