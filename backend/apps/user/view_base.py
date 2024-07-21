import json
import uuid
from abc import abstractmethod

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from py3ws.views.generic_view import GenericView
from py3ws.utils import utils as py3ws_utils

from apps.address.forms import AddressForm
from apps.document.forms import DocumentAttributeForm
from apps.document.models import DocumentType
from apps.hierarchy.forms import HierarchyForm
from apps.user import USER_TYPE_REQUIRED_FIELDS, USER_TYPE_COMPANY_REQUIRED_FIELDS
from apps.user.forms import GroupsForm, UserForm
from apps.user.models import UserHierarchy
from apps.user.view_utils import ViewUtils
from apps.user_func.client.forms import ProcessingAgreementForm
from apps.user_func.client.models import ProcessingAgreement, ClientAccessToken, ClientProcessingAgreement

from apps.document import utils as doc_utils

import apps.user.config as config
import apps.user.utils as user_utils
from py3ws.auth.decorators.decorators import p3permission_required


class UserException(Exception):
    pass


class UserManagement(GenericView):
    user_type = 'EMPLOYEE'

    def __init__(self):
        self.document_type = None
        self.attr = None

        self.user = None

        self.source = None
        self.override_base = None
        self.hierarchy = None

        self.initial = None
        self.initial_attributes = None

        self.form = None
        self.attr_form = None
        self.groups_form = None
        self.hierarchy_form = None
        self.companyaddress_form = None
        self.homeaddress_form = None
        self.mailaddress_form = None
        self.user_func_form = None
        self.processing_agreement_forms = []

        super().__init__()

    def set_app_name(self):
        self._app_name = 'user'

    def get_forms(self, data):

        if len(self.attr) > 0:
            self.attr_form = DocumentAttributeForm(data=data, document_type=self.document_type, defaults=False, prefix='attribute')

        self.form = UserForm(data=data,
                             files=data,
                             initial=self.initial,
                             user_type=self.user_type,
                             prefix='user',
                             mode=settings.MODE_CREATE)

        if self.user_type == 'CLIENT':
            for i in ProcessingAgreement.objects.filter(active=True, confirmation_date__isnull=False).order_by('sq'):
                self.processing_agreement_forms.append(ProcessingAgreementForm(data,
                                                                               prefix='agreement-%s' % i.pk,
                                                                               instance=i,
                                                                               initial={'agreement_checked': 1, 'source': None}))

        self.groups_form = GroupsForm(data=data)
        self.groups_form.fields['groups'].choices = Group.objects.all().order_by('name').values_list('id', 'name')
        self.hierarchy_form = HierarchyForm(data=data)
        self.companyaddress_form = AddressForm(data=data, prefix='companyaddress')
        self.homeaddress_form = AddressForm(data=data, prefix='homeaddress')
        self.mailaddress_form = AddressForm(data=data, prefix='mailaddress')
        self.user_func_form = ViewUtils.get_user_func_form(data=data,
                                                           initial=self.initial,
                                                           instance=None, type=self.user_type)

    def validate(self):
        valid = all([
            self.form.is_valid(),
            self.groups_form.is_valid(),
            self.companyaddress_form.is_valid(),
            self.homeaddress_form.is_valid(),
            self.mailaddress_form.is_valid()
        ])
        if self.attr_form:
            valid = valid and self.attr_form.is_valid()

        if self.user_func_form:  # and issubclass(user_func_form, p3wsModelForm):
            valid = valid and self.user_func_form.is_valid()

        for i in self.processing_agreement_forms:
            valid = valid and i.is_valid()

        return valid

    def _save_user(self, data):
        self.user = self.form.save(commit=False)
        self.user.username = user_utils.set_username(self.user.first_name, self.user.last_name, self.user.company_name)
        self.user.initial_password = user_utils.generate_password()
        self.user.set_password(self.user.initial_password)
        self.user.password_valid = False

        if self.user.email == '':
            self.user.email = None

        if self.companyaddress_form.has_changed():
            self.user.company_address = self.companyaddress_form.save()

        if self.homeaddress_form.has_changed():
            self.user.home_address = self.homeaddress_form.save()

        if self.mailaddress_form.has_changed():
            self.user.mail_address = self.mailaddress_form.save()

        avatar = data['files'].get('user-avatar', False)
        if avatar:
            file = ViewUtils.handle_uploaded_file(avatar)
            self.user.avatar_filename = file['file_name']
            self.user.avatar_base64 = file['file_base64']

        self.user.save()

        self.user.groups.set(self.groups_form.cleaned_data['groups'])
        self.user.save()

    def _save_hierarchy(self):
        if not self.user:
            raise UserException("_save_hierarchy: parametr user pusty")
        if self.hierarchy:
            self.user.hierarchy.clear()
            for h in self.form.cleaned_data['hierarchy']:
                UserHierarchy.objects.create(user=self.user, hierarchy=h)

    def _save_func_form(self):
        if not self.user:
            raise UserException("_save_hierarchy: parametr user pusty")
        if self.user_func_form:  # and issubclass(user_func_form, p3wsModelForm):
            cl = self.user_func_form.save(commit=False)
        else:
            cl = py3ws_utils.get_class('apps.user_func.' + self.user_type.lower() + '.models.' + self.user_type.capitalize())()
        cl.user = self.user
        cl.document_type = self.document_type
        cl.save()
        return cl

    def _save_attr_form(self):
        if self.attr_form:
            doc_utils.save_document_attributes(self.user.pk, self.document_type.pk, self.attr_form.cleaned_data)

    def _save_processing_agreements(self):
        for i in self.processing_agreement_forms:

            if i.has_changed():
                try:
                    cpa = ClientProcessingAgreement.objects.get(client=self.user.client, processing_agreement=i.instance)
                    cpa.source = i.cleaned_data.get('source')
                    cpa.value = i.cleaned_data.get('value')
                    cpa.save()

                except ClientProcessingAgreement.DoesNotExist:
                    ClientProcessingAgreement.objects.create(client=self.user.client,
                                                             processing_agreement=i.instance,
                                                             text=i.cleaned_data.get('text'),
                                                             source=i.cleaned_data.get('source'),
                                                             value=i.cleaned_data.get('value')
                                                             )

    def save(self, data):
        self._save_user(data)
        self._save_hierarchy()
        uf = self._save_func_form()
        self._save_attr_form()
        self._save_processing_agreements()
        # if self.user_type == 'CLIENT':
        #     ClientAccessToken.objects.create(client=uf, token=uuid.uuid4(), valid=True)

    def get_context(self, extra=None):
        context = {'form': self.form,
                   'attr': self.attr,
                   'attr_form': self.attr_form,
                   'document_type': DocumentType.objects.get(code='USER'),
                   'companyaddress_form': self.companyaddress_form,
                   'homeaddress_form': self.homeaddress_form,
                   'mailaddress_form': self.mailaddress_form,
                   'user_func_form': self.user_func_form,
                   'processing_agreement_forms': self.processing_agreement_forms,
                   'mode': self._mode,
                   'groups_form': self.groups_form,
                   'hierarchy_form': self.hierarchy_form,
                   'hierarchy': self.hierarchy,
                   'type': self.user_type,
                   'config': config.iframe if self.override_base else config.regular,
                   'override_base': self.override_base,
                   'USER_TYPE_REQUIRED_FIELDS': json.dumps(USER_TYPE_REQUIRED_FIELDS),
                   'USER_TYPE_COMPANY_REQUIRED_FIELDS': json.dumps(USER_TYPE_COMPANY_REQUIRED_FIELDS),
                   'errors': self.errors
                   }
        if extra:
            context = context.update(extra)

        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.errors = None
        try:
            self.user_type = self.kwargs['user_type']
        except KeyError:
            pass

        self.document_type = DocumentType.objects.get(code=self.user_type)

        self.override_base = settings.IFRAME_BASE_TEMPLATE if request.GET.get('iframe') == '1' else None
        self.document_type = doc_utils.get_document_type(code=self.user_type)
        self.hierarchy = ViewUtils.get_hierarchy(self.user_type)

        self.attr = doc_utils.get_attributes(self.document_type.pk)
        self.get_forms(request.POST or None)

        if request.method == 'POST':
            with transaction.atomic():
                if self.validate():
                    self.save({'post': request.POST, 'files': request.FILES})

                    if self.override_base:
                        return redirect('user.added_iframe')
                    else:
                        return redirect(self.user_type.lower() + '.list')
                else:
                    self.errors = GenericView.collect_errors(
                        [
                            self.form,
                            self.attr_form,
                            self.groups_form,
                            self.hierarchy_form,
                            self.companyaddress_form,
                            self.homeaddress_form,
                            self.mailaddress_form,
                            self.user_func_form] + (self.processing_agreement_forms or [])
                    )

        return render(request, self.template_name, self.get_context())


class UserSourceAbstract:
    def __init__(self, *args, **kwargs):
        self.source = self.get_source()
        self.initial_data = self.get_initial_data()
        self.document = None

    @abstractmethod
    def get_source(self):
        raise NotImplementedError

    @abstractmethod
    def get_user_type(self):
        raise NotImplementedError

    @abstractmethod
    def get_initial_data(self):
        raise NotImplementedError

    @abstractmethod
    def get_initial_attributes(self):
        raise NotImplementedError

    @abstractmethod
    def complete(self, client):
        raise NotImplementedError
