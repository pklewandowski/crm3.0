import os

from rest_framework.views import APIView

import crm_settings
from apps.document.models import Document
from apps.report.models import ReportTemplate


class DocumentReport(APIView):

    def get(self, request):
        pass

        # document = Document.objects.get(request.query_params.get('id'))
        # template = ReportTemplate.objects.get(request.query_params.get('idTemplate'))
        #
        #
        #
        # params = {'CODE': '1/2020', 'CREATION_DATE': '2020-01-01', 'CREATED_BY': 'Piotr Lewandowski'}
        # input_file = os.path.join(crm_settings.MEDIA_ROOT, 'reports/templates/xlsx/TCJDG_tmpl.xlsx')
        # output_file = os.path.join(crm_settings.MEDIA_ROOT, 'reports/generated/TCJDG_%s.xlsx' % uuid.uuid4())
        #
        # wb = openpyxl.load_workbook(input_file)
        # utils.fill_data(wb, 'DATA', {'C2': params['CODE'], 'C3': params['CREATION_DATE'], 'C4': params['CREATED_BY']})
        # wb.save(output_file)