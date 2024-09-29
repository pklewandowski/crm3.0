import traceback

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tag.api.serializers import TagSerializer
from apps.tag.models import Tag


class TagApi(APIView):
    def get(self, request):
        response_status = status.HTTP_200_OK
        response_data = {}
        try:
            response_data = [i.name for i in Tag.objects.all().order_by('name')]
        except Exception as ex:
            response_status = status.HTTP_400_BAD_REQUEST
            response_data = {"errmsg": str(ex), "traceback": traceback.format_exc()}

        return Response(data=response_data, status=response_status)
