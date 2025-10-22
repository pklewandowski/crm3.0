import traceback

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.document.models import DocumentType
from apps.document.utils import get_available_statuses


class DocumentTypeStatusApi(APIView):
    def get(self, request):
        response_data = {}
        response_status = status.HTTP_200_OK
        try:
            current_status = request.query_params.get('status', None)
            document_type = DocumentType.objects.get(pk=request.query_params.get('documentId'))
            available_statuses = get_available_statuses(type=document_type, status=current_status)
            if available_statuses:
                response_data = ((i.available_status.pk, i.available_status.name) for i in available_statuses)

        except Exception as ex:
            response_data['errmsg'] = str(ex)
            response_data['traceback'] = traceback.format_exc()
            response_status = status.HTTP_400_BAD_REQUEST

        return Response(data=response_data, status=response_status)
