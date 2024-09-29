import datetime
import json
import traceback

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Max, Count
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
from rest_framework import status as http_status

from apps.document.models import DocumentType
from apps.user.forms import UserCompleteForm
from apps.user_func import utils
from apps.user_func.adviser.models import Adviser
from apps.user_func.client.models import Client, ClientAccessToken
from py3ws.views import generic_view
from . import USER_TYPE_CODE

from .api.services import current_contacts_service
from .forms import ClientProcessingAgreementForm
from .models import ClientProcessingAgreement, ProcessingAgreement
from ...product.models import Product


def index(request):
    return HttpResponse("Tu będzie funkcjonalność zarządzania klientem.")


class ClientView(generic_view.GenericView):
    def set_app_name(self):
        self._app_name = 'user_func.client'

    def __init__(self):
        super(ClientView, self).__init__()


class List(generic_view.ListView):
    def set_mode(self):
        self._mode = settings.MODE_VIEW

    def set_app_name(self):
        self._app_name = 'user_func.client'

    def __init__(self):
        self.default_sort_field = 'user__last_name'
        self.document_code = USER_TYPE_CODE
        super(List, self).__init__()

    def set_query(self):
        self.query = Client.objects \
            .annotate(prod_max_creation_date=Max('product_set__creation_date'),
                      product_in_windication=Count('product_set', filter=Q(product_set__document__status__code__in=['WDK'])),
                      product_in_execution=Count('product_set', filter=Q(product_set__document__status__code__in=['WDK_EXEC'])),
                      product_active_count=Count('product_set', filter=Q(product_set__document__status__is_closing_process=False)),
                      product_count=Count('product_set')
                      ) \
            .filter(self.where) \
            .select_related('user', 'broker', 'adviser', 'company') \
            .prefetch_related('broker__user', 'adviser__user', 'product_set', ) \
            .order_by('%s%s' % (self.sort_dir, self.sort_field))

    def set_where(self):
        self.where = Q(user__is_active=True)

        if self.process_id:
            self.where &= Q(user__process_id=self.process_id)

        if self._user.has_perm('client.list:all'):
            pass
        elif self._user.has_perm('client.list:department'):
            self.where &= (Q(adviser__user__hierarchy__in=self._user.hierarchy.all()))
        elif self._user.has_perm('client.list:own'):
            self.where &= Q(adviser__user=self._user)
        else:
            raise PermissionDenied('Użytkownik nie ma uprawnień pozwalających na przeglądanie')

        if self.search:
            self.where &= (
                    Q(user__first_name__icontains=self.search) |
                    Q(user__last_name__icontains=self.search) |
                    Q(user__company_name__icontains=self.search) |
                    Q(user__nip__icontains=self.search) |
                    Q(user__krs__icontains=self.search) |
                    Q(user__phone_one__icontains=self.search) |
                    Q(user__email__icontains=self.search) |
                    Q(adviser__user__first_name__icontains=self.search) |
                    Q(adviser__user__last_name__icontains=self.search) |
                    Q(adviser__user__company_name__icontains=self.search) |
                    Q(adviser__user__nip__icontains=self.search) |
                    Q(adviser__user__krs__icontains=self.search) |
                    Q(adviser__user__phone_one__icontains=self.search) |
                    Q(adviser__user__email__icontains=self.search) |
                    Q(broker__user__first_name__icontains=self.search) |
                    Q(broker__user__last_name__icontains=self.search) |
                    Q(broker__user__company_name__icontains=self.search) |
                    Q(broker__user__nip__icontains=self.search) |
                    Q(broker__user__krs__icontains=self.search) |
                    Q(broker__user__phone_one__icontains=self.search) |
                    Q(broker__user__email__icontains=self.search) |
                    Q(user__tags__contains=[self.search.lower()])
            )

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        self.process_id = kwargs.pop('process_id', None)
        super(List, self).dispatch(request, *args, **kwargs)
        self.check_permissions(request.user)

        document_types = DocumentType.objects.filter(is_product=True, is_active=True).order_by('name')
        context = {'document_types': document_types}
        return self.list(request=request, template='user/_list.html', extra_context=context)


@transaction.atomic()
def add(request, id):
    return utils.add('apps.user_func.client.models.Client', id, USER_TYPE_CODE)


def get_list(request):
    # TODO: docelowo przenieść wybór ajax tekiego typu list do py3ws

    response_data = {'data': None, 'message': None}
    try:

        ids = json.loads(request.POST.get('id'))
        key = request.POST.get('key')

        if len(key) > 0:

            clients = Client.objects.filter(Q(user__first_name__icontains=key) |
                                            Q(user__last_name__icontains=key) |
                                            Q(user__personal_id__icontains=key) |
                                            Q(user__nip__icontains=key)).exclude(pk__in=ids).values('pk',
                                                                                                    'user__first_name',
                                                                                                    'user__last_name',
                                                                                                    'user__email',
                                                                                                    'user__personal_id',
                                                                                                    'user__nip')
            if clients:
                c_list = []
                for c in clients:
                    c_list.append(
                        {'pk': c['pk'], 'first_name': c['user__first_name'], 'last_name': c['user__last_name'], 'email': c['user__email'],
                         'personal_id': c['user__personal_id'], 'nip': c['user__nip']})

                response_data['data'] = c_list  # serializers.serialize("json", clients, fields=('pk', 'user__first_name', 'user__last_name'))

        response_data['status'] = 'OK'

    except Exception as e:
        response_data['status'] = 'ERROR'
        response_data['message'] = str(e)

    return HttpResponse(json.dumps(response_data), content_type="application/json")


class TokenNotValidException(Exception):
    pass


def complete(request, token):
    # token = request.GET.get('t')

    try:
        with transaction.atomic():
            if token is None:
                raise Exception('Brak tokena!')

            client_access_token = ClientAccessToken.objects.get(token=token)

            if not client_access_token.valid:
                raise TokenNotValidException('Token dostępu jest nieaktualny!')

            form = UserCompleteForm(data=request.POST or None, instance=client_access_token.client.user)
            processing_agreement_form = ClientProcessingAgreementForm(request.POST or None, prefix='processing_agreement')

            if request.method == 'POST':
                if all([form.is_valid(), processing_agreement_form.is_valid()]):
                    user = form.save(commit=False)
                    user.save()
                    client_access_token.valid = False
                    client_access_token.save()

                    for i in processing_agreement_form.cleaned_data:
                        if processing_agreement_form.cleaned_data[i]:
                            processing_agreement = ProcessingAgreement.objects.get(pk=i)
                            try:
                                cpa = ClientProcessingAgreement.objects.get(client=client_access_token.client, processing_agreement=processing_agreement)

                                cpa.text = processing_agreement.text
                                cpa.value = True
                                cpa.update_date = datetime.datetime.now()

                                cpa.save()

                            except ClientProcessingAgreement.DoesNotExist as ex:
                                ClientProcessingAgreement.objects.create(
                                    client=user.client,
                                    processing_agreement=processing_agreement,
                                    text=processing_agreement.text,
                                    source='WWW',
                                    value=True
                                )

                    return render(request, 'client/completed.html')

        context = {'form': form, 'processing_agreement_form': processing_agreement_form}
        return render(request, 'client/complete.html', context)

    except ClientAccessToken.DoesNotExist:
        return render(request, '500.html', status=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                      context={'override_base': 'iframe.html', 'exception': {'message': 'Autoryzacja zakończona niepowodzeniem: Podany token nie istnieje'}})

    except TokenNotValidException:
        return render(request, '500.html', status=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                      context={'override_base': 'iframe.html', 'exception': {'message': 'Token autoryzacyjny stracił ważność!'}})

    except Exception as e:
        return render(request, '500.html', status=http_status.HTTP_500_INTERNAL_SERVER_ERROR, context={'override_base': 'iframe.html', 'exception': {'message': str(e)}})


@login_required()
@csrf_exempt
def get_list_for_select2(request):
    response_data = {}
    response_status = http_status.HTTP_200_OK

    id = request.GET.get('id')
    exclude = request.GET.get('exclude', [])
    key = request.GET.get('q')

    try:
        if id:
            q = Q(pk=id)
        else:
            q = (
                    Q(user__first_name__icontains=key) |
                    Q(user__last_name__icontains=key) |
                    Q(user__company_name__icontains=key) |
                    Q(user__nip__icontains=key) |
                    Q(user__personal_id__icontains=key) |
                    Q(user__phone_one__icontains=key) |
                    Q(user__email__icontains=key)
            )
        if exclude:
            pass

        result = Client.objects.filter(q)
        # if users.count() > 500:
        #     response_data['results'] = []
        # else:
        response_data['results'] = [
            {
                'id': i.pk, 'text': (i.user.company_name + ' ' if i.user.company_name else '') +
                                    ((i.user.first_name + ' ' if i.user.first_name else '') + (i.user.last_name or ''))
            } for i in result]

    except Exception as e:
        response_status = http_status.HTTP_400_BAD_REQUEST
        response_data['errmsg'] = str(e)
        response_data['traceback'] = traceback.format_exc()

    return HttpResponse(json.dumps(response_data), content_type="application/json", status=response_status)


@login_required()
@csrf_exempt
def get_clients_for_adviser_select2(request):
    id = request.POST.get('id')
    response_data = {}
    response_status = http_status.HTTP_200_OK

    try:
        result = Client.objects.filter(adviser=Adviser.objects.get(pk=id))

        response_data = [{'id': i.pk, 'text': (i.user.first_name + ' ' if i.user.first_name else '') +
                                              (i.user.last_name or '') + ' ' + (i.user.phone_one or '')} for i in result]
    except Exception as e:
        response_status = http_status.HTTP_400_BAD_REQUEST
        response_data['errmsg'] = str(e)
        response_data['traceback'] = traceback.format_exc()

    return HttpResponse(json.dumps(response_data), content_type="application/json", status=response_status)


class CurrentContactsView(ListView):
    model = Client
    paginate_by = 10
    template_name = 'client/current_contacts.html'

    def get_queryset(self):
        queryset = current_contacts_service.get_queryset(self.request.user.id)

        return queryset
