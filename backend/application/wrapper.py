import traceback

from rest_framework import status
from rest_framework.response import Response

from py3ws.exceptions import RestApiException


def rest_api_wrapper(fn):
    def _wrapped(ref, request):
        response_status = status.HTTP_200_OK
        try:
            response_data = fn(ref, request) or {}

        # except RestApiException as ex:
        #     response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
        #     response_data = {
        #         'errmsg': str(ex),
        #         'errtype': ex.__class__.__name__,
        #         'traceback': traceback.format_exc()
        #     }

        except Exception as ex:
            response_status = status.HTTP_400_BAD_REQUEST
            response_data = {
                'errmsg': str(ex),
                'errtype': ex.__class__.__name__,
                'traceback': traceback.format_exc()
            }

        return Response(data=response_data, status=response_status)

    return _wrapped
