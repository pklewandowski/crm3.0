from django.core.management import BaseCommand

from apps.document.models import DocumentTypeAttribute

items = []


def _get_items_for_parent(parent, only_ids=False):
    for i in DocumentTypeAttribute.objects.filter(parent=parent):
        if i.is_section or i.is_column or i.is_combo:
            _get_items_for_parent(i, only_ids)
        else:
            items.append(i.pk if only_ids else i)
    return items


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-p', '--parent_id', action='store')
        parser.add_argument('-i', '--only_ids', action='store_true')

    def handle(self, *args, **kwargs):
        print('------------STARTING ATTRIBUTE FOR PARENT-------------')
        print('----------------------------------------------------\n')
        print('parent id:', kwargs['parent_id'])
        print('only ids:', kwargs['only_ids'])
        print('----------------GETTING DATA------------------')

        _get_items_for_parent(
            parent=DocumentTypeAttribute.objects.get(pk=kwargs['parent_id']),
            only_ids=kwargs['only_ids']
        )

        print(sorted(items, key=lambda x: int(x)), len(items))
