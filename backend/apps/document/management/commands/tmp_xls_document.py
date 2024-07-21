import os

import uuid
from pprint import pprint

from django.core.management import BaseCommand
from pandas.tests.io.excel.test_openpyxl import openpyxl

from crm import settings
from py3ws.xlsx import utils
from docx2pdf import convert


class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        wb = openpyxl.load_workbook(os.path.join(settings.MEDIA_ROOT, 'reports/templates/xlsx/TCJDG_tmpl.xlsx'))
        utils.replace_cell_value(wb, 'DATA', '[P_NR_WN_P]', '001/2020')
        path = os.path.join(settings.MEDIA_ROOT, 'reports/generated/TCJDG_%s.xlsx' % uuid.uuid4())
        wb.save(path)
