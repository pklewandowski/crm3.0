from .models import Adviser


class AdviserUtils:
    @staticmethod
    def get_for_select2(id):
        if not id:
            return []
        try:
            client = Adviser.objects.get(pk=id)
        except Adviser.DoesNotExist:
            return []
        return [(id, "%s %s" % (client.user.first_name, client.user.last_name)), ]

def get_adviser_name(id):
    if not id:
        return ''
    try:
        adv = Adviser.objects.get(pk=id)
        return "%s %s" % (adv.user.first_name, adv.user.last_name)
    except Adviser.DoesNotExist:
        return ''
