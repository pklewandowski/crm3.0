from django.core.management import BaseCommand

from apps.document.api.views import AttributeModel
from apps.document.models import DocumentType


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-t', '--document_type', action='store')

    def handle(self, *args, **kwargs):
        document_type = DocumentType.objects.get(pk=kwargs['document_type'])
        print(('Updating document of type: %s...' % document_type.name).encode('ascii', 'ignore').decode('ascii'), end='')
        AttributeModel().update_model(document_type=document_type)
        print('done')
