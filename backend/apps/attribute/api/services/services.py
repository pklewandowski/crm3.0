from apps.attribute.models import Attribute


def get_list():
    return Attribute.objects.all().order_by('name')
