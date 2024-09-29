import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, F
from django.http import HttpResponse
from django.utils import html
from django.views.decorators.csrf import csrf_exempt
from py3ws.views import generic_view


from apps.user_func import utils
from . import USER_TYPE_CODE
from .models import Adviser


def index(request):
    return HttpResponse("Adviser")


class ListView(generic_view.ListView):
    def set_mode(self):
        self._mode = settings.MODE_VIEW

    def set_app_name(self):
        self._app_name = 'user_func.adviser'

    def __init__(self):
        self.default_sort_field = 'user__last_name'
        self.document_code = USER_TYPE_CODE
        super(ListView, self).__init__()

    def set_where(self):
        self.where = Q(user__is_active=True)
        if self.search:
            self.where &= (
                    Q(user__first_name__icontains=self.search) |
                    Q(user__last_name__icontains=self.search) |
                    Q(user__phone_one__icontains=self.search) |
                    Q(user__email__icontains=self.search)
            )

    def set_query(self):
        self.query = Adviser.objects.filter(self.where).select_related('user'). \
            annotate(first_name=F('user__first_name'),
                     last_name=F('user__last_name'),
                     email=F('user__email'),
                     phone_one=F('user__phone_one'),
                     date_joined=F('user__date_joined')
                     ).order_by('%s%s' % (self.sort_dir, self.sort_field))

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        super(ListView, self).dispatch(request, *args, **kwargs)
        return self.list(request=request, template='user/_list.html')


@transaction.atomic()
def add(request, id):
    return utils.add('apps.user_func.adviser.models.Adviser', id, USER_TYPE_CODE)


@login_required()
@csrf_exempt
def get_list_for_select2(request):
    key = html.mark_safe(request.GET.get('q', None))
    id = request.GET.get('id', None)
    exclude = html.mark_safe(request.POST.get('exclude', None))
    response_data = {}
    response_status = 200

    q = Q(pk=id) if id else Q(user__is_active=True) & (Q(user__last_name__istartswith=key) | Q(user__phone_one__startswith=key)) if key else None
    if q and exclude:
        q = q.exclude(pk__in=exclude)

    try:
        result = Adviser.objects.filter(q)
        response_data['results'] = [{'id': i.pk, 'text': (i.user.first_name + ' ' if i.user.first_name else '') + (i.user.last_name or '')} for i in result]
    except Exception as e:
        status = 400
        response_data['errmsg'] = str(e)

    return HttpResponse(json.dumps(response_data), content_type="application/json", status=response_status)
