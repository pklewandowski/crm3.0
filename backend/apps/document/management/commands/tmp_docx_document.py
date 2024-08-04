import os
import uuid

from django.conf import settings
from django.core.management import BaseCommand

from py3ws.docx_utils.docx_utils import DocxUtils


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        doc = os.path.join(settings.MEDIA_ROOT, 'reports/docx/test_replace_with_keeping_formating.docx')
        doc = DocxUtils(doc).replace(
            '[P_CAT_NAME_P]',
            'Test zamiany treści placeholdera z zachowaniem formatowania'
        )
        path = os.path.join(
            settings.MEDIA_ROOT,
            'reports/generated/test_replace_with_keeping_formating_generated_%s.docx' % uuid.uuid4())
        doc.save(path)
