import datetime
import sys

from django.core.management.base import BaseCommand

import apps.message.utils as msg_utils
from apps.message.models import MessageQueue


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        messages = MessageQueue.objects.filter(is_sent=False)
        for message in messages:
            try:
                msg_utils.send_message(
                    to=message.recipients,
                    phones=message.phones,
                    subject=message.subject,
                    body=message.text,
                    sms_text=message.sms_text,
                    attachments=message.attachments
                )
                message.is_sent = True
                message.send_date = datetime.datetime.now()
                message.save()
                sys.stdout.write('[%s][%s] OK\n' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), message.pk))
            except Exception as ex:
                sys.stdout.write('[%s][%s] FAILED!!!\n%s\n' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), message.pk, str(ex)))
