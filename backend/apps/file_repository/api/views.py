from rest_framework.response import Response
from rest_framework.views import APIView

from apps.file_repository.services import services


class FileRepositoryView(APIView):
    def get(self, request):
        return Response(data=services.get_file(id=request.query_params.get('id')))

    def post(self, request):
        file = request.FILES.get('file')
        return Response(**services.add_file(data=request.data, report_file=file, user=request.user))
