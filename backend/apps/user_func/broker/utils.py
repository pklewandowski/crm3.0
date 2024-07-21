from .models import Broker


class BrokerUtils:
    @staticmethod
    def get_for_select2(id):
        if not id:
            return []
        try:
            result = Broker.objects.get(pk=id)
        except Broker.DoesNotExist:
            return []
        return [(id, "%s %s" % (result.user.first_name, result.user.last_name)), ]

def get_broker_name(id):
    if not id:
        return ''
    try:
        result = Broker.objects.get(pk=id)
        return "%s %s" % (result.user.first_name, result.user.last_name) \
               + " / %s" % result.user.company_name if result.user.company_name else ''
    except Broker.DoesNotExist:
        return ''
