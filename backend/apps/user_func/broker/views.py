import json
import traceback

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction, models
from django.db.models import Q, F, Sum, Subquery, OuterRef, Count
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status as http_status

from py3ws.db.subquery import SubQuerySum
from py3ws.views import generic_view

from apps.user_func import utils
from apps.user_func.adviser.models import Adviser
from . import USER_TYPE_CODE
from .models import Broker
from ...product.models import Product


def index(request):
    return HttpResponse("Broker")


class ListView(generic_view.ListView):
    def set_mode(self):
        self._mode = settings.MODE_VIEW

    def set_app_name(self):
        self._app_name = 'user_func.broker'

    def __init__(self):
        self.default_sort_field = 'user__last_name'
        self.document_code = USER_TYPE_CODE
        super(ListView, self).__init__()

    def set_where(self):
        self.where = Q(user__is_active=True)

        if self.process_id:
            self.where &= Q(user__process_id=self.process_id)

        if not self.request.user.has_perm('broker.list:all'):
            self.where &= Q(adviser__user=self.request.user) | Q(adviser__isnull=True)

        if self.search:
            self.where &= (
                    Q(user__first_name__icontains=self.search) |
                    Q(user__last_name__icontains=self.search) |
                    Q(user__phone_one__icontains=self.search) |
                    Q(user__email__icontains=self.search) |
                    Q(adviser__user__first_name__icontains=self.search) |
                    Q(adviser__user__last_name__icontains=self.search)
            )

    def set_query(self):

        products_no_annex = Product.objects.filter(client__broker__pk=OuterRef(name='pk'), document__annex__isnull=True)

        self.query = Broker.objects.filter(self.where). \
            annotate(first_name=F('user__first_name'),
                     last_name=F('user__last_name'),
                     email=F('user__email'),
                     phone_one=F('user__phone_one'),
                     date_joined=F('user__date_joined'),
                     total_value=Sum('client_broker__product_set__value'),
                     # total_value=SubQuerySum(name='value', queryset=products),
                     total_value_no_annex=SubQuerySum(name='value', queryset=products_no_annex)
                     ).select_related('user').order_by('%s%s' % (self.sort_dir, self.sort_field))
        print(self.query.query)

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        self.process_id = kwargs.pop('process_id', None)
        self.request = request
        super(ListView, self).dispatch(request, *args, **kwargs)
        return self.list(request=request, template='user/_list.html')


@transaction.atomic()
def add(request, id):
    return utils.add('apps.user_func.broker.models.Broker', id, USER_TYPE_CODE)


@csrf_exempt
def get_brokers_for_adviser(request):
    response_data = {'data': None, 'message': None}
    status = 200
    try:
        id = request.POST.get('id')
        if id == '':
            response_data['status'] = 'OK'
            return HttpResponse(json.dumps(response_data), content_type="application/json")

        response_data['data'] = [{'id': i.pk, 'name': (i.user.first_name or '') + ' ' + (i.user.last_name or '')}
                                 for i in Broker.objects.filter(user__is_active=True, adviser=Adviser.objects.get(pk=id))]
        response_data['status'] = 'OK'

    except Adviser.DoesNotExist as ex:
        pass
    except Exception as e:
        status = 400
        response_data['message'] = str(e)

    return HttpResponse(json.dumps(response_data), content_type="application/json", status=status)


@csrf_exempt
def get_brokers_for_adviser_select2(request):
    response_data = {}
    response_status = http_status.HTTP_200_OK
    try:
        id = request.POST.get('id')
        key = request.POST.get("q")
        if id == '':
            response_data['status'] = 'OK'
            return HttpResponse(json.dumps(response_data), content_type="application/json")

        q = Q(user__is_active=True, adviser=Adviser.objects.get(pk=id))
        q &= (Q(user__last_name__istartswith=key) | Q(user__phone_one__startswith=key))
        result = Broker.objects.filter(q)
        response_data['results'] = [{'id': i.pk, 'text': (i.user.first_name + ' ' if i.user.first_name else '') +
                                                         (i.user.last_name or '') + ' ' + (i.user.phone_one or '')} for i in result]

    except Exception as e:
        response_status = http_status.HTTP_400_BAD_REQUEST
        response_data = {'message': str(e), 'traceback': traceback.format_exc()}

    return HttpResponse(json.dumps(response_data), content_type="application/json", status=response_status)


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

        result = Broker.objects.filter(q)

        response_data['results'] = [
            {
                'id': i.pk, 'text': (i.user.first_name + ' ' if i.user.first_name else '') +
                                    ((i.user.first_name + ' ' if i.user.first_name else '') + (i.user.last_name or ''))
            } for i in result]

    except Exception as e:
        response_status = http_status.HTTP_400_BAD_REQUEST
        response_data = {'errmsg': str(e), 'traceback': traceback.format_exc()}

    return HttpResponse(json.dumps(response_data), content_type="application/json", status=response_status)
