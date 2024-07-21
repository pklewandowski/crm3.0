from apps.user_func.client.models import Client
from apps.widget.current_contacts.api.services import QUERY


def get_queryset(user_id):
    return Client.objects.raw(QUERY, params=[user_id, user_id, user_id, user_id])
