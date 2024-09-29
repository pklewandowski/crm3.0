import json
import pprint
from abc import abstractmethod

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from py3ws.forms.p3form import FilterForm
from py3ws.lists.rawpaginator import RawQuerySetPaginator
from py3ws.utils import utils as py3ws_utils
from py3ws.utils.utils import is_ajax


class GenericView(View):
    _app_name = None
    _has_any_permission = False
    _mode = None
    _context = {'config': {}}
    errors = []

    @abstractmethod
    def set_mode(self):
        raise NotImplementedError

    @abstractmethod
    def set_app_name(self):
        raise NotImplementedError

    def _get_main_classname(self):
        return ''.join(map(lambda x: x.capitalize(), self._app_name_last_part.split('_')))

    def __init__(self):
        super(GenericView, self).__init__()
        self.set_app_name()
        if not self._app_name:
            raise AttributeError('zmienna app_name nie może być pusta.')

        self.set_mode()
        if not self._mode:
            raise AttributeError('zmienna mode nie może być pusta.')

        self._context['config']['mode'] = self._mode

        self._app_name_last_part = self._app_name.split(".")[-1]
        self._main_app_classname = self._get_main_classname()

    def has_any_permissions(self, user):

        main_app_class = py3ws_utils.get_class('apps.%s.models.%s' % (self._app_name, self._main_app_classname))

        if not main_app_class:
            return
        try:
            permissions = main_app_class._meta.permissions
        except AttributeError:
            return

        if not permissions:
            self._has_any_permission = True
            return

        if user.is_superuser:
            self._has_any_permission = True
        else:
            for k, v in permissions:
                if user.has_perm('%s.%s' % (self._app_name_last_part, k)):
                    self._has_any_permission = True
                    return

    def check_permissions(self, user):
        self.has_any_permissions(user)
        if not self._has_any_permission:
            raise PermissionDenied

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @staticmethod
    def collect_errors(forms):
        error_list = {}
        for idx, form in enumerate(forms):
            if not form:
                continue
            errors = {}
            form_name = "%s_%s" % (form.form_name or '', idx) if hasattr(form, 'form_name') else "%s_%s" % (form.__class__.__name__, idx)  #
            for field in form:
                field_errors = field.errors
                if field_errors:
                    errors[field.label] = [err for err in field_errors]
            error_list[form_name] = errors
        return error_list


class ListView(GenericView):
    document_code = None
    document_type = None
    search = ''

    sort = ''
    sort_field = ''
    raw_sort = ''
    sort_dir = ''
    rows_per_page = 30

    query = None
    where = Q()
    page_number = 1
    default_sort_field = ''
    filter_form = None
    paginator = None
    _user = None

    def __init__(self):
        self.raw_sort, self.sort, self.sort_field = self.default_sort_field, self.default_sort_field, self.default_sort_field
        super(ListView, self).__init__()

    @abstractmethod
    def set_where(self):
        pass

    @abstractmethod
    def set_query(self):
        raise NotImplementedError()

    def list(self, request, template=None, extra_context=None):
        status = 200
        response_data = {}

        try:
            context = {'type': self.document_code,
                       'search': self.search,
                       'sort_field': self.sort_field,
                       'sort_dir': self.sort_dir}

            if is_ajax(request):
                context['page'] = {}
                context['page']['data'] = serializers.serialize('json', self.paginator.page(self.page_number))
                context['page']['number'] = self.page_number
                context['page']['num_pages'] = self.paginator.num_pages

            else:
                context['filter_form'] = self.filter_form
                context['page'] = self.paginator.page(self.page_number)

            if extra_context:
                context = py3ws_utils.merge_two_dicts(context, extra_context)

            if is_ajax(request):
                return HttpResponse(json.dumps(context), status=status)
            else:
                return render(request, template, context)

        except Exception as e:
            if is_ajax(request):
                response_data['errmsg'] = str(e)
                status = 400
                return HttpResponse(json.dumps(response_data), status=status)
            else:
                raise Exception(e)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self._user = request.user
        self.filter_form = FilterForm(request.POST or None, mode=settings.MODE_FILTER,
                                      initial={
                                          'p3_sort_field': self.default_sort_field,
                                          'p3_sort_dir': self.sort_dir
                                      },
                                      prefix='filter-form')

        if request.method == 'POST':
            if self.filter_form.is_valid():
                self.sort_field = self.filter_form.cleaned_data.get('p3_sort_field') or self.default_sort_field
                self.sort_dir = self.filter_form.cleaned_data.get('p3_sort_dir') or ''
                self.sort = self.sort_dir + self.sort_field
                self.raw_sort = self.sort_field + (' DESC' if self.sort_dir == '-' else '')
                self.search = self.filter_form.cleaned_data.get('search')
                self.page_number = int(self.filter_form.cleaned_data.get('page') or 1)
        self.set_where()
        self.set_query()
        self.paginator = RawQuerySetPaginator.Paginator(self.query, self.rows_per_page)
