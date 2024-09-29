from rest_framework.views import APIView

from application.wrapper import rest_api_wrapper
from apps.widget.current_contacts.api import services
from apps.user.api.services import services as user_services


class CurrentContacts(APIView):
    @rest_api_wrapper
    def get(self, request):
        # todo:
        # 1. Paginator
        # 2. Details

        if request.query_params.get('mode') == 'LIST':
            return services.get_list(request)

        elif request.query_params.get('mode') == 'DETAILS':
            return user_services.get_details(request)


class CurrentContactsDetails(APIView):
    def get(self, request):
        pass
