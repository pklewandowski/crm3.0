import base64

from django.utils.translation import gettext_lazy as _

from apps.document.models import Document
from py3ws.utils import utils as py3ws_utils
from apps.hierarchy.models import Hierarchy
from apps.scheduler.schedule.models import Schedule
from apps.product.models import Product
from django.conf import settings
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
import os
import uuid
import datetime


class ViewUtils:
    @staticmethod
    def get_user_func_form(data, type, initial=None, instance=None):
        if type not in ['CLIENT', 'BROKER', 'LAWOFFICE']:
            return None
        form_class = 'apps.user_func.' + type.lower() + '.forms.' + type.capitalize() + 'Form'
        return py3ws_utils.get_class(form_class)(data, prefix='user_func', initial=initial, instance=instance)

    @staticmethod
    def get_hierarchy(type):
        if type in ['EMPLOYEE', 'ADVISER']:
            hierarchy = Hierarchy.objects.get(type='ROOT').get_children()
            if not hierarchy:
                raise Exception(_('role.error.no_app_role'))
        else:
            hierarchy = None
        return hierarchy

    @staticmethod
    def handle_uploaded_file(f):
        file_name = uuid.uuid4().hex
        if not os.path.exists(settings.AVATAR_ROOT):
            os.makedirs(settings.AVATAR_ROOT)
        with open(file=settings.AVATAR_ROOT + '/' + file_name, mode='wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

        with open(settings.AVATAR_ROOT + '/' + file_name, "rb") as avatar_file:
            avatar_file_base64 = base64.b64encode(avatar_file.read()).decode()
        return {'file_name': file_name, 'file_base64': avatar_file_base64}

    @staticmethod
    def get_user_events(user, upcoming=False):
        q = Q()
        if upcoming:
            q = (Q(start_date__gte=datetime.datetime.now()) | Q(end_date__gte=datetime.datetime.now()))
        q = q & (Q(host_user=user) | Q(invited_users__in=[user]))

        events = Schedule.objects.filter(q).exclude(status__in=['AN', 'CL']).order_by("start_date")
        return events

    @staticmethod
    def get_user_products(user, active=False):

        q = Q(owner=user, type__is_product=True)
        if active:
            q &= Q(status__is_active=True, product__isnull=False)
        try:

            products = Document.objects.filter(q).order_by('-creation_date')
        except ObjectDoesNotExist:
            return None

        return products
