import pprint
import sys
import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
import apps.message.utils as msg_utils


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        try:
            msg_utils.send_message(to=[settings.ADMIN_EMAIL], subject='Proces msg_queue busy!', body='sprawdź dlaczego!')
            sys.stdout.write('[%s] sent message process busy\n' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
        except Exception as ex:
            sys.stdout.write('[%s] FAILED!!!\n%s\n' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), str(ex)))
