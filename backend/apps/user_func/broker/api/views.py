import json
import traceback
import uuid

from django.db.models import Q
from rest_framework import status as http_status, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.user_func.adviser.models import Adviser
from apps.user_func.broker.models import Broker
from apps.user_func.csv import services
from py3ws.csvutl import csvutl
from py3ws.csvutl.validator import CsvValidatorException


@api_view(['GET'])
def get_list_for_select2(request):
    key = request.query_params.get('q', None)
    id = request.query_params.get('id', None)
    exclude = request.query_params.get('exclude', None)

    response_data = {}
    response_status = http_status.HTTP_200_OK

    q = Q(pk=id) if id else Q(user__is_active=True) & (
            Q(user__last_name__icontains=key) |
            Q(user__first_name__icontains=key) |
            Q(user__phone_one__icontains=key)
    ) if key else Q()

    if q and exclude:
        q = q.exclude(pk__in=exclude)

    try:
        result = Broker.objects.filter(q)
        response_data['results'] = [{'id': i.pk, 'text': (i.user.first_name + ' ' if i.user.first_name else '') + (i.user.last_name or '')} for i in result]

    except Exception as e:
        response_status = http_status.HTTP_400_BAD_REQUEST
        response_data = {'errmsg': str(e), 'traceback': traceback.format_exc()}

    return Response(response_data, status=response_status)


class BrokersForAdviser(APIView):
    def get(self, request):
        response_data = {}
        response_status = http_status.HTTP_200_OK

        try:
            id = request.query_params.get('id', None)
            key = request.query_params.get("q", None)

            q = Q(user__is_active=True)

            if id:
                q &= Q(adviser=Adviser.objects.get(pk=id))

            if key:
                q &= (
                        Q(user__last_name__icontains=key) |
                        Q(user__first_name__icontains=key) |
                        Q(user__phone_one__icontains=key)
                )

            response_data['results'] = [{'id': i.pk, 'text': (i.user.first_name + ' ' if i.user.first_name else '') +
                                                             (i.user.last_name or '')} for i in Broker.objects.filter(q)]

        except Exception as e:
            response_status = http_status.HTTP_400_BAD_REQUEST
            response_data = {'message': str(e), 'traceback': traceback.format_exc()}

        return Response(response_data, status=response_status)


class BrokerCsv(APIView):
    def get(self, request):
        return Response(data='not implemented yet')

    def post(self, request):
        response_status = status.HTTP_201_CREATED
        response_data = {}

        if 'csv_process_id' not in request.session or not request.session['csv_process_id']:
            request.session['csv_process_id'] = str(uuid.uuid4())

        response_data['processId'] = request.session['csv_process_id']

        try:
            valid = True
            csv_header = list(map(lambda x: x['csv_header'], services.HEADER))
            file = request.FILES['file'].read().decode('utf-8-sig')

            csv_process_result = csvutl.process_csv(data=file, source_header=csv_header, validators=csvutl.build_validators(csv_schema=services.HEADER))
            if csv_process_result['errors']:
                valid = False

            client_batch_upload = services.CsvBatchUpload(process_id=request.session['csv_process_id'], user=request.user)

            valid &= client_batch_upload.load_users_into_buffer_table(data=csv_process_result['data'])

            response_data['header'] = csv_header

            # only bad rows are presented to the user
            response_data['data'] = list(filter(lambda i: i['__errors__'], csv_process_result['data']))

            if valid:
                client_batch_upload.upload('BROKER')
                del request.session['csv_process_id']

            else:
                response_data['errmsg'] = 'Plik zawiera błędy'
                response_status = status.HTTP_400_BAD_REQUEST

        except CsvValidatorException as ex:
            response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
            response_data = json.loads(str(ex))

        except Exception as ex:
            response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            response_data = {"errmsg": str(ex), "traceback": traceback.format_exc()}

        return Response(data=response_data, status=response_status)


def download(request):
    return services.download()
