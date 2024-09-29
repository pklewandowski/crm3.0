import json

from rest_framework.views import APIView

from application.wrapper import rest_api_wrapper
from apps.document.models import Document
from apps.product.api.instalment_schedule import services


class ProductInstalmentScheduleView(APIView):
    @rest_api_wrapper
    def get(self, request):
        return services.recalculate(user=request.user, opts=json.loads(request.query_params.get('opts')))


class ProductInstalmentScheduleMappingView(APIView):
    @rest_api_wrapper
    def get(self, request):
        return services.get_mapping(Document.objects.get(pk=request.query_params.get('idDocument')))
