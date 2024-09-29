from django.core.management import BaseCommand
from django.db import transaction

from apps.document.models import DocumentTypeAttribute, DocumentType
from apps.config.models import FormAttribute
from apps.attribute.models import Attribute


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        attr = FormAttribute.objects.get(form_name='document').attributes
        document_type = DocumentType.objects.get(pk=26)

        def f(at):
            for i in at:
                natr = DocumentTypeAttribute.objects.create(
                    id=i['id'],
                    sq=i['sq'],
                    lov=i['lov'],
                    code=i['code'],
                    name=i['name'],
                    parent=DocumentTypeAttribute.objects.get(pk=i['parent']) if i['parent'] else None,
                    feature=i['feature'],
                    is_table=i['is_table'],
                    attribute=Attribute.objects.get(pk=i['attribute']['id']) if 'attrtibute' in i and 'id' in i['attribute'] else None,
                    css_class=i['css_class'],
                    hierarchy=i['hierarchy'],
                    is_column=i['is_column'],
                    is_section=i['is_section'],
                    description=i['description'],
                    is_required=i['is_required'],
                    placeholder=i['placeholder'],
                    document_type=document_type,
                    type='FORM'
                )
                if 'children' in i:
                    f(i['children'])

        with transaction.atomic():
            f(attr)
