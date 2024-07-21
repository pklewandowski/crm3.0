import datetime
import re

from apps.message.utils import send_message
from apps.notification.models import Notification as NotificationModel, NotificationUser, NotificationTemplate


class NotificationException(Exception):
    pass


class Notification:
    def __init__(self, user_list, template_code=None, text=None, params=None, document=None, user=None, effective_date=datetime.date.today()):
        self.template = NotificationTemplate.objects.get(code=template_code) if template_code else None
        self.user_list = user_list
        self.params = params
        self._text = text
        self.document = document
        self.user = user
        self.effective_date = effective_date

        self.text = None

    def __bind_params(self):
        txt = self._text or (self.template.text if self.template.text else None)

        if not txt:
            # TODO: LOG WARNING WITH EMAIL TO ADMIN
            return

        # bind parameters delivered in params param
        if isinstance(self.params, dict):
            for k, v in self.params.items():
                txt = txt.replace('$P__%s__P$' % k, v)

        # bind formal parameters like DOCUMENT, USER, DATE, etc
        p = list(map(lambda x: {x[0]: x[1]}, re.findall(r"\$P__(DOCUMENT|PRODUCT|USER|DATE)\.*([a-zA-Z0-9_]*)__P\$", txt)))
        for i in p:
            if self.document and 'DOCUMENT' in i:
                v = str(getattr(self.document, i['DOCUMENT'].lower()))
                txt = txt.replace('$P__DOCUMENT.%s__P$' % i['DOCUMENT'], v)

            elif self.document and 'PRODUCT' in i:
                product = self.document.product
                v = str(getattr(product, i['PRODUCT'].lower()))
                txt = txt.replace('$P__PRODUCT.%s__P$' % i['PRODUCT'], v)

            elif self.user and 'USER' in i:
                v = str(getattr(self.document, i['USER'].lower()))
                txt = txt.replace('$P__USER.%s__P$' % i['USER'], v)

            elif 'DATE' in i:
                txt = txt.replace('$P__DATE__P$', datetime.datetime.strftime(datetime.datetime.today(), '%Y-%m-%d'))

        self.text = txt

    def bind_params(self):
        return self.__bind_params()

    def register(self):
        self.__bind_params()

        notification = NotificationModel.objects.create(
            template=self.template,
            text=self.text,
            effective_date=self.effective_date
        )
        for i in self.user_list:
            if not i:
                continue
            NotificationUser.objects.create(
                notification=notification,
                user=i,
                status='NW',
            )

    @staticmethod
    def get(id):
        try:
            return NotificationModel.objects.get(pk=id)
        except NotificationModel.DoesNotExist:
            return None

    @staticmethod
    def status(id, user, status):
        notification = NotificationUser.objects.get(notification=NotificationModel.objects.get(pk=id), user=user)
        notification.status = status
        notification.save()
