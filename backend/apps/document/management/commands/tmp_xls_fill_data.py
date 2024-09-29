import os
import uuid

import openpyxl
from django.core.management import BaseCommand

import crm_settings
from py3ws.msoffice.xlsx import utils



class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        params = {'CODE': '1/2020', 'CREATION_DATE': '2020-01-01', 'CREATED_BY': 'Piotr Lewandowski'}
        input_file = os.path.join(crm_settings.MEDIA_ROOT, 'reports/templates/xlsx/TCJDG_tmpl.xlsx')
        output_file = os.path.join(crm_settings.MEDIA_ROOT, 'reports/generated/TCJDG_%s.xlsx' % uuid.uuid4())

        wb = openpyxl.load_workbook(input_file)
        utils.fill_data(wb, 'DATA', {'C2': params['CODE'], 'C3': params['CREATION_DATE'], 'C4': params['CREATED_BY']})
        wb.save(output_file)
