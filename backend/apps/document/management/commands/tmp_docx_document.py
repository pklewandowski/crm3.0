import os
import re
import uuid
from pprint import pprint

from django.core.management import BaseCommand

from crm import settings
from py3ws.docx import utils
from docx import Document
from docx2pdf import convert


class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        doc = Document(os.path.join(settings.MEDIA_ROOT, 'reports/templates/docx/alamakota_tmpl.docx'))
        utils.docx_replace(doc, '[P_CAT_NAME_P]', 'Sierściuch jebany')
        path = os.path.join(settings.MEDIA_ROOT, 'reports/generated/alamakota_generated_%s.docx' % uuid.uuid4())
        doc.save(path)
        convert(path, path + '.pdf')
