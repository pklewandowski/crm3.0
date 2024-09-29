import copy
from pprint import pprint

from django.core.management import BaseCommand
from django.db import transaction, connection

from apps.document.models import DocumentType, DocumentTypeAccounting, DocumentTypeStatus, DocumentTypeProcessFlow
from apps.document.api.attribute_utils import AttributeUtils


class Command(BaseCommand):
    def add_arguments(self, parser):
        # parser.add_argument('-x', nargs='+', type=str)
        parser.add_argument('-s', '--source_document_type', action='store')
        parser.add_argument('-c', '--new_document_code', action='store')
        parser.add_argument('-n', '--new_document_name', action='store')

    def handle(self, *args, **kwargs):
        return
        print('------------STARTING DOCUMENT TYPE COPY-------------')
        print('----------------------------------------------------\n')
        print('old document type:', kwargs['source_document_type'])
        print('new document name:', kwargs['new_document_name'])

        # DocumentType.objects.get(pk=44).delete()
        # return

        with transaction.atomic():
            source_document_type = DocumentType.objects.get(pk=kwargs['source_document_type'])
            document_type_accounting = DocumentTypeAccounting.objects.filter(document_type=source_document_type)
            document_type_status = DocumentTypeStatus.objects.filter(type=source_document_type)

            document_type = copy.copy(source_document_type)
            document_type.pk = None
            document_type.name = kwargs['new_document_name']
            document_type.save()

            DocumentType.objects.raw('CREATE SEQUENCE crm.document_type_id_%s_sq' % document_type.pk)

            print('new document_type pk:', document_type.pk)

            for i in document_type_accounting:
                i.pk = None
                i.document_type = document_type
                i.save()

            status_mapping = {}
            for i in document_type_status:
                status = i.pk
                i.pk = None
                i.type = document_type
                i.save()
                status_mapping[status] = i.pk

            print(list(status_mapping.keys()))

            for i in DocumentTypeProcessFlow.objects.filter(status__in=DocumentTypeStatus.objects.filter(pk__in=list(status_mapping.keys()))):
                print(i, status_mapping[i.status.pk])
                i.status = DocumentTypeStatus.objects.get(pk=status_mapping[i.status.pk])
                i.available_status = DocumentTypeStatus.objects.get(pk=status_mapping[i.available_status.pk])
                i.pk = None
                i.save()

            AttributeUtils.copy_attributes(source_document_type=source_document_type, new_document_type=document_type)
