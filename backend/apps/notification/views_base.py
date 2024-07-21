from django.conf import settings
from py3ws.views.generic_view import GenericView


class NotificationView(GenericView):
    def set_mode(self):
        self._mode = settings.MODE_CREATE

    def set_app_name(self):
        self._app_name = 'notification'
