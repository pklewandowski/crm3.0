from django import template

from apps.hierarchy.models import HierarchyPosition
from apps.user.models import UserHierarchyPosition, User

register = template.Library()


@register.filter(name='is_user_hierarchy_position')
def is_user_hierarchy_position(id, user):
    try:
        UserHierarchyPosition.objects.get(user=user, position=HierarchyPosition.objects.get(pk=id))
    except UserHierarchyPosition.DoesNotExist:
        return False
    return True
