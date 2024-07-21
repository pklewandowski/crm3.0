import json
import pprint

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, resolve_url

# Create your views here.
from django.urls import reverse
from django.utils import html
from django.views.decorators.csrf import csrf_exempt

from apps.config.models import HoldingCompany
from apps.document import utils as doc_utils
from apps.document.models import DocumentType, DocumentTypeStatus, Document, DocumentAttribute, DocumentTypeAttribute

from apps.marketing.partner.forms import PartnerLeadForm, PartnerAgreementFormset
from apps.marketing.partner.models import PartnerLeadAgreement, PartnerLead, PartnerAgreement
from apps.marketing.partner.views_base import PartnerView, PartnerException

from py3ws.views.generic_view import ListView

from apps.user.models import User
from apps.user_func.broker.models import Broker
from apps.user_func.client.models import Client


class List(ListView):
    def set_mode(self):
        self._mode = settings.MODE_VIEW

    def set_app_name(self):
        self._app_name = 'marketing.partner'

    def __init__(self):
        self.default_sort_field = 'creation_date'
        self.sort_dir = "-"
        super(List, self).__init__()

    def set_query(self):
        self.query = PartnerLead.objects.filter(self.where).select_related('security_type').order_by('%s%s' % (self.sort_dir, self.sort_field)).exclude(status='DL')

    def set_where(self):
        self.where = Q()
        if self._user.has_perm('partner.list:all'):
            pass
        elif self._user.has_perm('partner.list:own'):
            self.where &= Q(adviser=self._user.adviser_set)
        else:
            raise PermissionDenied('Użytkownik nie ma zdefiniowanych uprawnień do przeglądania listy ParnterLead')

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        self.rows_per_page = 30
        super().dispatch(request, *args, **kwargs)
        context = {"agreement_list": [i.text for i in PartnerAgreement.objects.filter(is_active=True).order_by('sq')]}
        return self.list(request=request, template='partner/list.html', extra_context=context)


class Add(PartnerView):
    def set_mode(self):
        self._mode = settings.MODE_CREATE

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        status = 200
        response_data = {}

        try:
            Add.validate_request(request)

            form = PartnerLeadForm(request.POST)
            agreement_formset = PartnerAgreementFormset(data=request.POST, queryset=PartnerLeadAgreement.objects.all(), prefix='agreement')

            if all([form.is_valid(), agreement_formset.is_valid()]):
                with transaction.atomic():
                    lead = Add.save_lead(form, agreement_formset)
                    Add.notify(lead)

            else:
                response_data['form_errors'] = form.errors
                response_data['agreement_formset_errors'] = agreement_formset.errors
                status = 400
                # TODO: LOG błędu + wysłanie wiadomości do administratora systemu - log('tekst', admin_message=True) lub np. admin_log('tekst')

        except Exception as ex:
            status = 400
            response_data['errmsg'] = str(ex)
            # TODO: ZALOGUJ + ALERT DO ADMINISTRATORA

        return HttpResponse(json.dumps(response_data), content_type="application/json", status=status)


class AddBroker(PartnerView):
    def set_mode(self):
        self._mode = settings.MODE_CREATE

    @csrf_exempt
    @transaction.atomic()
    def dispatch(self, request, *args, **kwargs):
        id = self.kwargs.pop('id', None)
        if not id:
            raise PartnerException('AddBroker: pusty leadId')

        lead = PartnerLead.objects.get(pk=id)

        try:
            user = User.objects.get(email=lead.email)
        except User.DoesNotExist:
            user = User.objects.create(
                first_name=lead.partner_first_name.capitalize(),
                last_name=lead.partner_last_name.capitalize(),
                phone_one=lead.partner_phone,
                email=lead.partner_email
            )

        broker = Broker.objects.create(
            user=user,
            adviser=lead.adviser,
            document_type=DocumentType.objects.get(code='BROKER')
        )

        lead.broker = broker
        lead.save()

        for i in PartnerLead.objects.filter(email=lead.partner_email, broker__isnull=True).exclude(status='DL'):
            i.broker = broker
            i.save()

        return redirect('user.edit', user.pk, 'BROKER')


class AddUser(PartnerView):
    user_type = None

    def set_mode(self):
        self._mode = settings.MODE_CREATE

    def _get_lead(self, id):
        if not id:
            raise PartnerException('Partner: pusty leadId')
        self.lead = PartnerLead.objects.get(pk=id)

        if self.lead.status == 'CL':
            raise PartnerException("Lead posiada status ['CL'] niepozawalający na utworzenie dokumentu pożyczki")

        if getattr(self.lead, self.user_type.lower()):
            raise PartnerException('Lead posiada już %s' % self.user_type)

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        id = self.kwargs.pop('id', None)
        if not id:
            raise PartnerException('pusty leadId')
        self._get_lead(id)

        return redirect(to='user.add', user_type=self.user_type, source_code=self.SOURCE_CODE, source_id=self.lead.pk)


class AddClient(AddUser):
    def __init__(self):
        self.user_type = 'CLIENT'
        super().__init__()


class AddPartner(AddUser):
    def __init__(self):
        self.user_type = 'BROKER'
        super().__init__()


class AddDocument(PartnerView):
    lead = None
    document = None
    document_type = None

    def set_mode(self):
        self._mode = settings.MODE_CREATE

    def _get_lead(self, id):
        if not id:
            raise PartnerException('Partner: pusty leadId')
        self.lead = PartnerLead.objects.get(pk=id)

        if self.lead.status == 'CL':
            raise PartnerException("Lead posiada status ['CL'] niepozawalający na utworzenie dokumentu pożyczki")

        if not self.lead.broker:
            raise PartnerException('Lead nie posiada brokera')

        if not self.lead.broker.adviser:
            raise PartnerException('Pośrednik nie posiada doradcy')

        if not self.lead.client:
            raise PartnerException('Lead nie posiada klienta')

    @staticmethod
    def _get_document_type():
        return DocumentType.objects.get(code='PZ1')

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        self._get_lead(self.kwargs.pop('id', None))
        self.document_type = AddDocument._get_document_type()

        return redirect('document.add', self.document_type.pk, self.SOURCE_CODE, self.lead.pk)


class Status(PartnerView):
    def set_mode(self):
        self._mode = settings.MODE_EDIT

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        status = 200
        response_data = {}
        id = html.mark_safe(request.POST.get('id'))
        lead_status = html.mark_safe(request.POST.get('status'))
        try:
            lead = PartnerLead.objects.get(pk=id)
            lead.status = lead_status
            lead.save()
        except Exception as ex:
            status = 400
            response_data['errmsg'] = str(ex)
        return HttpResponse(json.dumps(response_data), content_type='application/json', status=status)
