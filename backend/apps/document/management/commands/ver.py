#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management import BaseCommand
from django.db import transaction

from apps.document.api.attribute_utils import AttributeUtils
from apps.document.models import DocumentTypeStatus, DocumentTypeAttribute, DocumentTypeAttributeFeature


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-p', '--parent', action='store', default=None)
        parser.add_argument('-c', '--status_code', action='store', default=None)
        parser.add_argument('-f', '--ver', action='store', default=None)

    def handle(self, *args, **kwargs):
        print('------------------ Starting VER --------------------')

        parent = DocumentTypeAttribute.objects.get(pk=kwargs['parent'])
        document_type = parent.document_type

        status = DocumentTypeStatus.objects.get(code=kwargs['status_code'], type=document_type)
        visible, editable, required = kwargs['ver'][0] == 'Y', kwargs['ver'][1] == 'Y', kwargs['ver'][2] == 'Y'

        print(f'Document: {document_type.name}')
        print(f'Parent node: {parent.name}')
        print(f'Setting VER for status: {status.name}')

        with transaction.atomic():
            attributes = []

            AttributeUtils.get_attribute_list(document_type=document_type, parent=parent, level=attributes)

            for attribute in attributes:
                try:
                    feature = DocumentTypeAttributeFeature.objects.get(attribute=attribute, status=status)
                    feature.visible = visible
                    feature.editable = editable
                    feature.required = required

                except DocumentTypeAttributeFeature.DoesNotExist:
                    feature = DocumentTypeAttributeFeature(attribute=attribute, status=status, visible=visible, editable=editable, required=required)

                feature.save()

        print('-------------------- Done VER ----------------------')
