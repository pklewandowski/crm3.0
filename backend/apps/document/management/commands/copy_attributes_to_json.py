import json
from django.core.management import BaseCommand
from rest_framework.serializers import ModelSerializer
from apps.document.models import DocumentType, DocumentTypeAttribute


class DocumentTypeAttributeSerializer(ModelSerializer):
    class Meta:
        model = DocumentTypeAttribute
        exclude = ('id', 'parent', 'hierarchy', 'document_type')


class Command(BaseCommand):
    def add_arguments(self, parser):
        # parser.add_argument('-x', nargs='+', type=str)
        parser.add_argument('-t', '--document_type', action='store')
        parser.add_argument('-s', '--source_parent', action='store')
        parser.add_argument('-f', '--file_name', action='store')

    def handle(self, *args, **kwargs):
        model = {
            "__meta": {
                "document_type": kwargs['document_type'],
                "source_parent": kwargs['source_parent'],
            }, "attributes": []}

        document_type = DocumentType.objects.get(pk=kwargs['document_type'])
        source_parent = DocumentTypeAttribute.objects.get(pk=kwargs['source_parent']) if kwargs['source_parent'] else None

        def f(m, parent=None):
            attributes = DocumentTypeAttribute.objects.filter(document_type=document_type, parent=parent)
            for i in attributes:
                serializer = DocumentTypeAttributeSerializer(i)
                m.append(serializer.data)
                if DocumentTypeAttribute.objects.filter(document_type=document_type, parent=i).count():
                    m[-1]['_children'] = []
                    f(m[-1]['_children'], i)

        f(model["attributes"], source_parent)

        file = open(kwargs['file_name'], 'wb')
        file.write(json.dumps(model).encode('utf8', 'ignore'))

