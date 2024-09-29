import pprint
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from apps.marketing.lp.forms import MediumForm, SourceForm, LeadPageForm
from apps.marketing.lp.models import PageEntry, Medium, Source, LeadPage
from crm import settings
from django.shortcuts import render, redirect

# Create your views here.
from py3ws.views.generic_view import ListView, GenericView


def index(request):
    return HttpResponse('lp index')


class List(ListView):
    def set_mode(self):
        self._mode = settings.MODE_VIEW

    def set_app_name(self):
        self._app_name = 'marketing.lp'

    def __init__(self):
        self.default_sort_field = 'created'
        self.sort_dir = "-"
        super(List, self).__init__()

    def set_query(self):
        self.query = PageEntry.objects.all().select_related('source', 'medium').order_by('%s%s' % (self.sort_dir, self.sort_field))

    def set_where(self):
        self.where = Q()

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        self.rows_per_page = 30
        super().dispatch(request, *args, **kwargs)
        context = {}
        return self.list(request=request, template='lp/list.html', extra_context=context)


class ManageLp(GenericView):
    form = None
    template_name = None

    def __init__(self):
        super().__init__()

    def set_app_name(self):
        self._app_name = 'marketing.lp'

    @transaction.atomic()
    def dispatch(self, request, *args, **kwargs):

        if self.form.is_valid():
            self.form.save()
            redirect(request, 'marketing.lp.medium.list')

        context = {'form': self.form}
        return render(request, self.template_name, context=context)


class AddMedium(ManageLp):
    def set_mode(self):
        self._mode = settings.MODE_CREATE

    def __init__(self):
        self.form = MediumForm()
        self.template_name = 'lp/medium/add.html'
        super().__init__()

    def dispatch(self, request, *args, **kwargs):
        self.form = MediumForm(request.POST or None)
        return super().dispatch(request, *args, **kwargs)


class EditMedium(ManageLp):
    def set_mode(self):
        self._mode = settings.MODE_EDIT

    def __init__(self):
        self.form = MediumForm()
        self.template_name = 'lp/medium/edit.html'
        super().__init__()

    @transaction.atomic()
    def dispatch(self, request, *args, **kwargs):
        id = self.kwargs('id')

        self.form.instance = Medium.objects.get(pk=id)
        return super().dispatch(request, *args, **kwargs)


class ListMedium(ListView):
    pass


class AddSource(ManageLp):
    def set_mode(self):
        self._mode = settings.MODE_CREATE

    def __init__(self):
        self.form = SourceForm()
        self.template_name = 'lp/source/add.html'
        super().__init__()

    def dispatch(self, request, *args, **kwargs):
        self.form = SourceForm(request.POST or None)
        return super().dispatch(request, *args, **kwargs)


class EditSource(ManageLp):
    def set_mode(self):
        self._mode = settings.MODE_EDIT

    def __init__(self):
        self.form = SourceForm()
        self.template_name = 'lp/source/edit.html'
        super().__init__()

    @transaction.atomic()
    def dispatch(self, request, *args, **kwargs):
        id = self.kwargs('id')
        self.form.instance = Source.objects.get(pk=id)
        return super().dispatch(request, *args, **kwargs)


class ListSource(ListView):
    pass


class AddLeadPage(ManageLp):
    def set_mode(self):
        self._mode = settings.MODE_CREATE

    def __init__(self):
        self.template_name = 'lp/lead_page/add.html'
        super().__init__()

    def dispatch(self, request, *args, **kwargs):
        self.form = LeadPageForm(request.POST or None)
        return super().dispatch(request, *args, **kwargs)


class EditLeadPage(ManageLp):
    def set_mode(self):
        self._mode = settings.MODE_EDIT

    def __init__(self):
        self.form = LeadPageForm()
        self.template_name = 'lp/lead_page/edit.html'
        super().__init__()

    @transaction.atomic()
    def dispatch(self, request, *args, **kwargs):
        id = self.kwargs('id')
        self.form.instance = LeadPage.objects.get(pk=id)
        return super().dispatch(request, *args, **kwargs)


class ListLeadPage(ListView):
    pass
