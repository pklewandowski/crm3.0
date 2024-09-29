import copy

from django.core.management import BaseCommand
from django.db import transaction

from apps.document.models import DocumentType, DocumentTypeAttribute
from apps.document.api.attribute_utils import AttributeUtils


class Command(BaseCommand):
    def add_arguments(self, parser):
        # parser.add_argument('-x', nargs='+', type=str)
        parser.add_argument('-s', '--source_document_type', action='store')
        parser.add_argument('-d', '--dest_document_type', action='store')
        parser.add_argument('-p', '--source_parent', action='store')
        parser.add_argument('-c', '--dest_parent', action='store')
        parser.add_argument('-i', '--include_parent', action='store_true')

    def handle(self, *args, **kwargs):
        print('------------STARTING ATTRIBUTE COPY-------------')
        print('----------------------------------------------------\n')
        print('source document type:', kwargs['source_document_type'])
        print('dest document name:', kwargs['dest_document_type'])
        print('source parent:', kwargs['source_parent'])
        print('dest_parent:', kwargs['dest_parent'])
        print('include_parent', kwargs['include_parent'])
        print('----------------COPYING ATTRIBUTES------------------')

        source_document_type = DocumentType.objects.get(pk=kwargs['source_document_type'])
        dest_document_type = DocumentType.objects.get(pk=kwargs['dest_document_type'])
        source_parent = DocumentTypeAttribute.objects.get(pk=kwargs['source_parent']) if kwargs['source_parent'] else None
        dest_parent = DocumentTypeAttribute.objects.get(pk=kwargs['dest_parent']) if kwargs['dest_parent'] else None

        with transaction.atomic():
            if kwargs['include_parent']:
                parent = copy.copy(source_parent)
                parent.pk = None
                parent.code = None
                parent.parent = dest_parent

                parent.save()
                parent.code = parent.pk
                parent.save()

                dest_parent = parent

            AttributeUtils.copy_attributes(
                source_document_type=source_document_type,
                new_document_type=dest_document_type,
                parent_node=source_parent,
                new_parent_node=dest_parent
            )
