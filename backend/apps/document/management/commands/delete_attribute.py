from pprint import pprint

from django.core.management import BaseCommand
from apps.document.models import DocumentTypeAttribute


class Command(BaseCommand):
    def add_arguments(self, parser):
        # parser.add_argument('-x', nargs='+', type=str)
        parser.add_argument('-a', '--attribute_id', action='store')
        parser.add_argument('-p', '--is_parent', action='store_true')

    def handle(self, *args, **kwargs):

        attribute = DocumentTypeAttribute.objects.get(pk=kwargs['attribute_id'])
        q = input('Are U sure to delete attibute id: %s name: %s (yes/N)?' % (attribute.pk, attribute.name))

        if q == 'yes':
            if kwargs['is_parent']:
                for i in DocumentTypeAttribute.objects.filter(parent=attribute):
                    print('deleting attribute: ', i.pk, i.name)
                    i.delete()
            else:
                attribute.delete()
            print('AttributeApi and its children deleted!')
        elif q == 'N':
            print('Quit not deleted!')
        else:
            print('Wrong answer')
