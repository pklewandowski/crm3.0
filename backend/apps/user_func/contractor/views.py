import json
import traceback

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Max, Count
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from py3ws.views import generic_view

from apps.document.models import DocumentType
from apps.user.forms import UserForm
from apps.user_func import utils
from apps.user_func.adviser.models import Adviser
from apps.user_func.client.models import Client, ClientAccessToken
from apps.user_func.contractor.models import Contractor

from . import USER_TYPE_CODE


def index(request):
    return HttpResponse("Tu będzie funkcjonalność zarządzania klientem.")


class ContractorView(generic_view.GenericView):
    def set_app_name(self):
        self._app_name = 'user_func.contractor'

    def __init__(self):
        super().__init__()


class List(generic_view.ListView):
    def set_app_name(self):
        self._app_name = 'user_func.contractor'

    def set_mode(self):
        self._mode = settings.MODE_VIEW

    def __init__(self):
        self.default_sort_field = 'user__last_name'
        self.document_code = USER_TYPE_CODE
        super().__init__()

    def set_query(self):
        self.query = Contractor.objects.filter(self.where).select_related('user').order_by('%s%s' % (self.sort_dir, self.sort_field))

    def set_where(self):
        self.where = Q(user__is_active=True)

        if self._user.has_perm('contractor.list:all'):
            pass
        elif self._user.has_perm('contractor.list:department'):
            self.where &= (Q(adviser__user__hierarchy__in=self._user.hierarchy.all()))
        elif self._user.has_perm('contractor.list:own'):
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
                    Q(user__email__icontains=self.search)
            )

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        super(List, self).dispatch(request, *args, **kwargs)
        self.check_permissions(request.user)

        document_types = DocumentType.objects.filter(is_product=True, is_active=True).order_by('name')
        context = {'document_types': document_types}
        return self.list(request=request, template='user/_list.html', extra_context=context)


@transaction.atomic()
def add(request, id):
    return utils.add('apps.user_func.contractor.models.Contractor', id, USER_TYPE_CODE)


def get_list(request):
    # TODO: docelowo przenieść wybór ajax tekiego typu list do py3ws

    response_data = {'data': None, 'message': None}
    try:

        ids = json.loads(request.POST.get('id'))
        key = request.POST.get('key')

        if len(key) > 0:

            contractors = Contractor.objects.filter(Q(user__first_name__icontains=key) |
                                                    Q(user__last_name__icontains=key) |
                                                    Q(user__personal_id__icontains=key) |
                                                    Q(user__nip__icontains=key)).exclude(pk__in=ids).values('pk',
                                                                                                            'user__first_name',
                                                                                                            'user__last_name',
                                                                                                            'user__email',
                                                                                                            'user__personal_id',
                                                                                                            'user__nip')
            if contractors:
                c_list = []
                for c in contractors:
                    c_list.append(
                        {'pk': c['pk'], 'first_name': c['user__first_name'], 'last_name': c['user__last_name'], 'email': c['user__email'],
                         'personal_id': c['user__personal_id'], 'nip': c['user__nip']})

                response_data['data'] = c_list  # serializers.serialize("json", clients, fields=('pk', 'user__first_name', 'user__last_name'))

        response_data['status'] = 'OK'

    except Exception as e:
        response_data['status'] = 'ERROR'
        response_data['message'] = str(e)

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@login_required()
@csrf_exempt
def get_list_for_select2(request):
    key = request.GET.get('q')
    id = request.GET.get('id', None)
    add_query = json.loads(request.GET.get('addQuery')) if request.GET.get('addQuery') else None
    response_data = {}
    status = 200

    if id:
        q = Q(pk=id)
    else:
        q = (
                Q(user__last_name__icontains=key) |
                Q(user__company_name__icontains=key) |
                Q(user__nip__icontains=key) |
                Q(user__personal_id__icontains=key) |
                Q(user__phone_one__icontains=key)
        )
        if add_query:
            for i in add_query:
                q &= Q(**{'%s%s' % (i['field'], ('__%s' % i['operator']) if i['operator'] else ''): i['values']})

    try:
        result = Contractor.objects.filter(q)
        # if users.count() > 500:
        #     response_data['results'] = []
        # else:
        response_data['results'] = [
            {
                'id': i.pk, 'text': ((i.user.first_name + ' ' if i.user.first_name else '') + (i.user.last_name or '')) +
                                    (' (' + i.user.company_name + ')' if i.user.company_name else '')
            } for i in result]
    except Exception as e:
        status = 400
        response_data['errmsg'] = str(e)
        response_data['traceback'] = traceback.format_exc()

    return HttpResponse(json.dumps(response_data), content_type="application/json", status=status)
