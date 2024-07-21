import json
import os
import traceback
import uuid

from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import crm_settings
from apps.user_func.csv import services
from py3ws.csvutl import csvutl
from py3ws.csvutl.validator import CsvValidatorException


class ClientCsv(APIView):
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

            # As chardet doesn't support windows-1250 encoding recognition it's useless now
            # file = request.FILES['file'].read()
            # encoding = chardet.detect(file)['encoding']
            # print('file encoding', encoding)
            # if encoding and not encoding.startswith('UTF-8'):
            #     encoding = 'windows-1250'
            # print('file encoding after', encoding)
            # file = file.decode(encoding if encoding else 'UTF-8-SIG')

            csv_process_result = csvutl.process_csv(data=file, source_header=csv_header, validators=csvutl.build_validators(csv_schema=services.HEADER))
            if csv_process_result['errors']:
                valid = False

            client_batch_upload = services.CsvBatchUpload(process_id=request.session['csv_process_id'], user=request.user)

            valid &= client_batch_upload.load_users_into_buffer_table(data=csv_process_result['data'])

            response_data['header'] = csv_header

            # only bad rows are presented to the user
            response_data['data'] = list(filter(lambda i: i['__errors__'], csv_process_result['data']))

            if valid:
                client_batch_upload.upload('CLIENT')
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
