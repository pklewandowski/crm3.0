from .models import Client


def get_client(id):
    if not id:
        return None
    try:
        client = Client.objects.get(pk=id)
        return client
    except Client.DoesNotExist:
        return None


class ClientUtils:
    @staticmethod
    def get_for_select2(id):
        client = get_client(id)
        if client:
            return [(id, "%s %s" % (client.user.first_name, client.user.last_name)), ]
        else:
            return []
