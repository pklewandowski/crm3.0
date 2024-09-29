import datetime
import sys

from django.core.management.base import BaseCommand
from django.db.models import Max

import apps.message.utils as msg_utils
from apps.marketing.lp import MAX_LP_NONACTIVITY_TIMEOUT
from apps.marketing.lp.models import PageEntry
from apps.message.models import MessageQueue, MessageTemplate
from apps.user.models import User


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        now = datetime.datetime.now()
        if 19 < now.hour < 23 or 0 < now.hour < 7:
            sys.stdout.write('[%s] current time out of range of interest\n' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
            return
        try:
            max_created = PageEntry.objects.aggregate(max_created=Max('created'))['max_created']
            if max_created:

                dl = datetime.datetime.now() - max_created
                if dl.days > 1 or (dl.seconds / 60 / 60) > MAX_LP_NONACTIVITY_TIMEOUT:
                    msg_utils.register_message(
                        template=MessageTemplate.objects.get(code='NO_LP_ACTIVITY_ALERT'),
                        add_params={'LAST_LP_ENTRY_DATE': str(max_created)},
                        recipients=['piotr.lewandowski@speedcashpolska.pl'],
                        phones=['603163167']
                    )
                    sys.stdout.write('{} {} days {:.0f} hours LP NOT UPCOMMING!\n'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), dl.days, dl.seconds / 60 / 60))
                else:
                    sys.stdout.write('[%s][%s] [%s] OK!\n' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), dl.days, dl.dl.seconds / 60 / 60))
        except Exception as ex:
            sys.stdout.write('[%s] FAILED!!!\n%s\n' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), str(ex)))
