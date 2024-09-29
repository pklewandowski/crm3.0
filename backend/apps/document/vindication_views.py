from django.conf import settings
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from py3ws.views import generic_view

from apps.document.models import Document, DocumentTypeStatus
from apps.product.models import Product


class ListView(generic_view.ListView):
    def set_mode(self):
        self._mode = settings.MODE_VIEW

    def set_app_name(self):
        self._app_name = 'product'

    def __init__(self):
        self.default_sort_field = 'creation_date'
        self.sort_dir = '-'
        self.rows_per_page = 30

        super(ListView, self).__init__()

    def set_where(self):
        self.where = Q(document__product__status__code__istartswith=('WDK'))
        user = self.request.user

        if self.search:
            self.where &= (Q(document__code__icontains=self.search) |
                           Q(document__owner__first_name__icontains=self.search) |
                           Q(document__owner__last_name__icontains=self.search) |
                           Q(document__owner__company_name__icontains=self.search) |
                           Q(document__owner__phone_one__icontains=self.search) |
                           Q(document__owner__nip__icontains=self.search) |
                           Q(document__owner__personal_id__icontains=self.search) |
                           Q(document__owner__email__icontains=self.search) |
                           Q(document__created_by__first_name__icontains=self.search) |
                           Q(document__created_by__last_name__icontains=self.search)
                           )

    def set_query(self):
        self.query = Product.objects.filter(self.where).select_related('document').order_by('%s%s' % (self.sort_dir, self.sort_field))

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        self.document_type = self.kwargs['type']
        # self.has_any_permissions(request.user)
        # if not self.has_any_permission:
        #     raise PermissionDenied
        super(ListView, self).dispatch(request, *args, **kwargs)
        # self.check_permissions(request.user)
        return self.list(request=request, template='document/vindication/list.html')
