from django.test import TestCase, SimpleTestCase

# Create your tests here.
from apps.document.models import Document
from apps.notification.utils import Notification
from apps.user.models import User


class NotificationTestCase(TestCase):
    databases = ['test']
    def setup(self):
        print('Notification parameter binding test...')
        user_list = [User.objects.get(pk=1)]
        user = User.objects.get(pk=3655)
        text = '''
        param entry parameter aircraft alphabet: $P__ALFA_BRAVO_CHARLIE_DELTA__P$,
        document code: $P__DOCUMENT.CODE__P$,
        document owner: $P__DOCUMENT.OWNER__P$,
        current date: $P__DATE__P$, 
        product start date: $P__PRODUCT.START_DATE__P$,
        '''
        document = Document.objects.get(pk=2013)
        self.notification = Notification(
            user_list=user_list,
            params={'ALFA_BRAVO_CHARLIE_DELTA': 'ABCD'},
            text=text, document=document,
            user=user)

    def bind_params_test(self):
        self.notification.bind_params()

# python .\manage.py test apps.notification.tests.NotificationTestCase
