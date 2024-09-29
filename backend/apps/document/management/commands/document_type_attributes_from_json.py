import json
from django.core.management import BaseCommand
from rest_framework.serializers import ModelSerializer

from apps.attribute.models import Attribute
from apps.document.models import DocumentType, DocumentTypeAttribute


class DocumentTypeAttributeSerializer(ModelSerializer):
    class Meta:
        model = DocumentTypeAttribute
        exclude = ('id', 'parent')


class Command(BaseCommand):
    def add_arguments(self, parser):
        # parser.add_argument('-x', nargs='+', type=str)
        parser.add_argument('-t', '--document_type', action='store')
        parser.add_argument('-s', '--source_parent', action='store')
        parser.add_argument('-f', '--file_name', action='store')

    def handle(self, *args, **kwargs):

        f = open(kwargs['file_name'])

        attributes = json.loads(f.read(), encoding='utf8')

        document_type = DocumentType.objects.get(pk=kwargs['document_type'])
        source_parent = DocumentTypeAttribute.objects.get(pk=kwargs['source_parent']) if kwargs['source_parent'] else None

        if DocumentTypeAttribute.objects.filter(parent=source_parent).count():
            r = input("Section not empty. Type 'yes' to continue")

            if r != 'yes':
                return

        def f(attr, parent=None):

            for i in attr:
                at = DocumentTypeAttribute()
                at.parent = parent
                for key, val in i.items():
                    if not key.startswith('_') and key not in ('attribute', 'code'):
                        setattr(at, key, val)

                if i['attribute']:
                    at.attribute = Attribute.objects.get(pk=i['attribute'])
                at.document_type = document_type
                at.save()
                at.code = str(at.id)
                at.save()

                if "_children" in i:
                    f(i["_children"], at)

        f(attributes["attributes"], source_parent)
