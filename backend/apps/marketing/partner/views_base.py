import json
from pprint import pprint

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Q, Func, F
from django.db.models.functions import Coalesce, datetime
from django.views import View

import py3ws.utils.validators as py3ws_validators

from apps.document.models import DocumentType
from apps.document.utils import DocumentSourceAbstract, DocumentSourceException
from apps.notification.utils import Notification
from apps.marketing.partner.models import PartnerLead
from apps.user.models import User
from apps.user.view_base import UserSourceAbstract
from apps.user_func.broker.models import Broker
from apps.user_func.client.models import Client
from py3ws.utils.utils import is_ajax
from py3ws.views.generic_view import GenericView


class PartnerException(Exception):
    pass


class PartnerView(GenericView):
    SOURCE_CODE = 'PARTNER'

    def set_app_name(self):
        self._app_name = 'marketing.partner'

    def __init__(self):
        super().__init__()

    @staticmethod
    def validate_request(request):
        if not request.method == 'POST':
            raise PartnerException('wymagany request.POST')
        if not is_ajax(request):
            raise PartnerException('wymagany AJAX request')

    @staticmethod
    def validate_lead(lead):
        errors = []

        try:
            validate_email(lead.email)
        except ValidationError as ex:
            errors.append('Niepoprawny adres e-mail klienta!')

        try:
            validate_email(lead.partner_email)
        except ValidationError as ex:
            errors.append('Niepoprawny adres e-mail partnera!')

        try:
            py3ws_validators.nip_validator(lead.nip)
        except ValidationError as ex:
            errors.append('Niepoprawny numer NIP!')
        return errors

    @staticmethod
    def match_broker(lead: PartnerLead):
        if not lead.partner_email:
            return None
        try:
            return Broker.objects.get(user__email=lead.partner_email)
        except Broker.DoesNotExist:
            return None

    @staticmethod
    def match_client(lead: PartnerLead):
        if not lead.nip and not lead.email:
            return None

        client = None

        if lead.nip:
            try:
                client = Client.objects.get(user__nip=lead.nip)
            except Client.DoesNotExist:
                pass
        if lead.email:
            try:
                client = Client.objects.get(user__email=lead.email)
            except Client.DoesNotExist:
                pass

        return client

    @staticmethod
    def save_lead(form, agreement_formset):
        lead = form.save(commit=False)

        errors = PartnerView.validate_lead(lead)
        if errors:
            raise PartnerException(json.dumps(errors))

        lead.broker = PartnerView.match_broker(lead)
        lead.client = PartnerView.match_client(lead)
        lead.adviser = lead.broker.adviser if lead.broker else None
        lead.save()

        for agreement_form in agreement_formset:
            agreement = agreement_form.save(commit=False)
            agreement.lead = lead
            agreement.check_date = datetime.datetime.now()
            agreement.save()

        return lead

    @staticmethod
    def notify(lead):
        user_list = list(filter(None, [lead.broker.user if lead.broker else None,
                                       lead.adviser.user if lead.adviser else None,
                                       lead.client.user if lead.client else None,
                                       ]))
        params = {
            'BROKER_RECOGNIZE': str(lead.broker) if lead.broker else 'nierozpoznany',
            'ADVISER_RECOGNIZE': str(lead.adviser) if lead.adviser else 'nierozpoznany',
            'CLIENT_RECOGNIZE': str(lead.client) if lead.client else 'nierozpoznany',
            'LEAD_DATE': datetime.datetime.strftime(lead.creation_date, '%Y-%m-%d %H:%M:%S'),
            'LEAD_ID': str(lead.pk)
        }
        if not user_list:
            from apps.marketing.partner import CC_PARNTER_LEAD_GROUP
            user_list = User.objects.filter(groups__name=CC_PARNTER_LEAD_GROUP)

        if not user_list:
            return

        Notification(user_list=user_list, template_code='NEW_PARTNER_LEAD', params=params).register()


class UserSource(UserSourceAbstract):
    INITIAL_DATA = None

    def __init__(self, *args, **kwargs):
        id = kwargs.pop('id')
        self.lead = PartnerLead.objects.get(pk=id)
        super().__init__(*args, **kwargs)

    def get_user_type(self):
        raise NotImplementedError

    def get_initial_attributes(self):
        return {}

    def get_initial_data(self):
        initials = {}
        for i, v in self.INITIAL_DATA.items():
            value = self.lead
            for j in i.split('.'):
                value = getattr(value, j)
                initials[v] = value
        return initials

    def complete(self, user):
        raise NotImplementedError

    def get_source(self):
        return self


class ClientSource(UserSource):
    INITIAL_DATA = {
        'first_name': 'first_name',
        'last_name': 'last_name',
        'company_name': 'company_name',
        'phone': 'phone_one',
        'email': 'email',
        'partner_email': 'partner_email'
    }

    def get_user_type(self):
        return 'CLIENT'

    def complete(self, client):
        if not client:
            raise DocumentSourceException('DocumentLead: Obiekt klienta nie może być pusty')
        self.lead.status = self.lead.CLOSE_STATUS
        self.lead.client = client
        self.lead.save()


class ParnterSource(UserSource):

    INITIAL_DATA = {
        'partner_first_name': 'first_name',
        'partner_last_name': 'last_name',
        'partner_company_name': 'company_name',
        'partner_phone': 'phone_one',
        'partner_email': 'email'
    }

    def get_user_type(self):
        return 'PARTNER'

    def complete(self, broker):
        if not broker:
            raise DocumentSourceException('DocumentLead: Obiekt klienta nie może być pusty')
        self.lead.status = self.lead.CLOSE_STATUS
        self.lead.broker = broker
        self.lead.save()


class DocumentSource(DocumentSourceAbstract):
    BROKER_ATTRIBUTE_CODE = '1_7925cfd835f84fe8a34d53e304ab4640'
    LENDER_ATTRIBUTE_CODE = '1_1cab84ff2eb1417aba79d27acdeeadc2'
    LENDER = 'ASCFIN'
    ATTRIBUTES = {
        'amount': '1_bc8ed3b4a06548c1a0adc38cfa25baae',
        'period': '1_0b7aa4a24d1a4bdba09cf41e7f0924d9',
        'broker.pk': '1_96d12f8f4eea41a6b7222d4a4ac1e95a',
        'broker.adviser.pk': '1_7481de1bee294fd5a4b6bf9103e7fbf4'
    }

    def __init__(self, *args, **kwargs):
        id = kwargs.pop('id')
        self.lead = PartnerLead.objects.get(pk=id)
        super().__init__(*args, **kwargs)

    def get_document_type(self):
        return DocumentType.objects.get(code='PZ1')

    def get_initial_attributes(self):
        attributes = {}
        for i, v in self.ATTRIBUTES.items():
            value = self.lead
            for j in i.split('.'):
                value = getattr(value, j)
            attributes[v] = value
        attributes[self.BROKER_ATTRIBUTE_CODE] = 'BRK'
        attributes[self.LENDER_ATTRIBUTE_CODE] = self.LENDER
        return attributes

    def complete(self, document):
        if not document:
            raise DocumentSourceException('DocumentLead: Obiekt dokumentu nie może być pusty')
        self.lead.status = self.lead.CLOSE_STATUS
        self.lead.document = document
        self.lead.save()

    def get_initial_data(self):
        return {'owner': self.lead.client.user}

    def get_source(self):
        return self
