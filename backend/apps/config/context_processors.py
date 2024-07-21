import sys

from apps.notification.models import NotificationUser
from apps.user.models import User


def get_cookies(request):
    side_menu_state = request.COOKIES.get('side_menu_state')
    return {'side_menu_state': side_menu_state}

def get_default_encoding(request):
    return {'default_encoding': sys.getdefaultencoding()}
