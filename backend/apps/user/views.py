import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Permission, ContentType, Group
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.validators import validate_email
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import html
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt

import apps.user.utils as user_utils
import py3ws.utils.validators as py3ws_validators
from apps.address.forms import AddressForm
from apps.document import utils as doc_utils
from apps.document.forms import DocumentAttributeForm
from apps.document.models import DocumentType, DocumentSource
from apps.hierarchy.models import Hierarchy
from apps.message import utils as msg_utils
from apps.message.models import MessageTemplate
from apps.scheduler.schedule.models import Schedule
from apps.user.forms import UserForm, PermissionForm, ChangePasswordForm, GroupForm, GroupsForm, UserRelationForm
from apps.user.models import User, UserHierarchy
from apps.user.view_base import UserManagement, UserException
from apps.user_func.adviser.models import Adviser
from apps.user_func.broker.models import Broker
from apps.user_func.client.forms import ProcessingAgreementForm
from apps.user_func.client.models import Client, ProcessingAgreement, ClientProcessingAgreement
from py3ws.auth.decorators.decorators import p3permission_required
from py3ws.utils import utils as py3ws_utils
from . import USER_TYPE_REQUIRED_FIELDS, USER_TYPE_COMPANY_REQUIRED_FIELDS
from .view_utils import ViewUtils


# from ..user_func.lawoffice.models import LawOffice


def _get_group_permissions_for_model(group_id, app_label, model):
    return [i.pk for i in Permission.objects.filter(group__id=group_id, content_type__in=ContentType.objects.filter(app_label=app_label, model=model))]


def index(request):
    return HttpResponse("user.index")


@login_required()
@p3permission_required('user.list_user')
@csrf_exempt
def list(request, process_id=None):
    q = Q(is_superuser=False)
    if process_id:
        q &= Q(process_id=process_id)
    users = User.objects.filter(q)

    context = {'users': users, 'mode': settings.MODE_EDIT}
    return render(request, 'user/list.html', context)


def inactive(request):
    return HttpResponse("Użytkownik jest nieaktywny")


def _save_processing_agreements(processing_agreement_forms, user):
    for i in processing_agreement_forms:

        if i.has_changed():
            try:
                cpa = ClientProcessingAgreement.objects.get(client=user.client, processing_agreement=i.instance)
                cpa.source = i.cleaned_data.get('source')
                cpa.value = i.cleaned_data.get('value')
                cpa.save()

            except ClientProcessingAgreement.DoesNotExist:
                ClientProcessingAgreement.objects.create(client=user.client,
                                                         processing_agreement=i.instance,
                                                         text=i.cleaned_data.get('text'),
                                                         source=i.cleaned_data.get('source'),
                                                         value=i.cleaned_data.get('value')
                                                         )


class Add(UserManagement):
    def __init__(self):
        self.template_name = 'user/add.html'
        self.initial = {}
        super().__init__()

    def set_mode(self):
        self._mode = settings.MODE_CREATE

    def _get_source(self):
        try:
            source_code = self.kwargs.pop('source_code', None)
            source_id = self.kwargs.pop('source_id')
        except KeyError:
            source_code = None
            source_id = None

        if source_code:
            if not source_id:
                raise UserException('Podano source_type_id a nie podano source_id')

            document_source = DocumentSource.objects.get(code=source_code, document_type=2)

            source_class = py3ws_utils.get_class(document_source.class_name)(id=source_id)
            self.source = source_class.get_source()

    def _get_initials(self):
        if self.source:
            self.initial = self.source.get_initial_data()
            self.initial_attributes = self.source.get_initial_attributes()
            if self.user_type == 'CLIENT':
                if 'partner_email' in self.initial and self.initial['partner_email']:
                    try:
                        broker = Broker.objects.get(user__email=self.initial['partner_email'])
                        self.initial['adviser'] = broker.adviser
                        self.initial['broker'] = broker

                    except Broker.DoesNotExist:
                        pass
                    del self.initial['partner_email']
        if self.user_type == 'LAWOFFICE':
            self.initial = {'is_company': True}

    def dispatch(self, request, *args, **kwargs):
        self.user_type = kwargs.pop('user_type')
        self._get_source()
        self._get_initials()

        return super().dispatch(request, *args, **kwargs)


def added_iframe(request):
    return render(request, 'user/added_iframe.html')


def _check_permission(user, request_user, type):
    user_hierarchy = [i.pk for i in user.hierarchy.all()]
    request_user_hierarchy = request_user.hierarchy.all()

    if type == 'CLIENT':
        if request_user.has_perm('client.change:all'):
            return
        elif request_user.has_perm('client.change:department'):
            return
        elif request_user.has_perm('client.change:own'):
            if user.client.adviser.user != request_user:
                raise PermissionDenied


@login_required()
@transaction.atomic()
def edit(request, id, type=None):
    user = User.objects.get(pk=id)

    _check_permission(user, request.user, type)

    if user.is_superuser:
        raise Exception('Użytkownik posiadający rolę \'SUPERUSER\' nie może być edytowany za pośrednictwem aplikacji')

    hierarchy = ViewUtils.get_hierarchy(type)

    if type:
        document_type = doc_utils.get_document_type(type)
        attr = doc_utils.get_attributes(document_type.pk)
        if len(attr) > 0:
            attr_values = doc_utils.get_document_attribute_values(id=id, id_type=document_type.pk)
            attr_form = DocumentAttributeForm(data=request.POST or None, document_type=document_type, defaults=False, prefix='attribute', initial=attr_values)
        else:
            attr = None
            attr_form = None
    else:
        document_type = None
        attr = None
        attr_form = None

    if type == 'CLIENT':
        user_func_form_instance = Client.objects.get(pk=user.pk)
    elif type == 'BROKER':
        user_func_form_instance = Broker.objects.get(pk=user.pk)
    else:
        user_func_form_instance = None

    form = UserForm(data=request.POST or None, prefix='user', instance=user, user_type=type, mode=settings.MODE_EDIT)
    user_relation_form = UserRelationForm(prefix='userrelation')

    processing_agreement_forms = []

    if type == 'CLIENT':
        for i in ProcessingAgreement.objects.filter(active=True, confirmation_date__isnull=False).order_by('sq'):
            try:
                cpa = ClientProcessingAgreement.objects.get(client=user.client, processing_agreement=i)
                value = cpa.value
                source = cpa.source
            except ClientProcessingAgreement.DoesNotExist:
                value = None
                source = None
            processing_agreement_forms.append(ProcessingAgreementForm(request.POST or None,
                                                                      prefix='agreement-%s' % i.pk,
                                                                      instance=i,
                                                                      initial={'value': value, 'source': source}))

    companyaddress_form = AddressForm(data=request.POST or None, instance=user.company_address, prefix='companyaddress')
    homeaddress_form = AddressForm(data=request.POST or None, instance=user.home_address, prefix='homeaddress')
    mailaddress_form = AddressForm(data=request.POST or None, instance=user.mail_address, prefix='mailaddress')

    user_func_form = ViewUtils.get_user_func_form(data=request.POST or None, instance=user_func_form_instance, type=type)

    groups = [i.pk for i in user.groups.all()]

    groups_form = GroupsForm(data=request.POST or None, initial=({'groups': groups}))
    groups_form.fields['groups'].choices = Group.objects.all().order_by('name').values_list('id', 'name')
    form.fields['username'].widget.attrs['readonly'] = True

    user_upcoming_events = ViewUtils.get_user_events(user, upcoming=True)
    user_all_events = ViewUtils.get_user_events(user)
    user_products = ViewUtils.get_user_products(user)
    user_active_products = ViewUtils.get_user_products(user, True)

    q = Q(url_name='user.edit', parameter_list__icontains=('"id": "' + str(user.id) + '"'))
    if type:
        q &= Q(parameter_list__icontains=type)

    if request.method == 'POST':
        valid = all([
            form.is_valid(),
            groups_form.is_valid(),
            companyaddress_form.is_valid(),
            homeaddress_form.is_valid(),
            mailaddress_form.is_valid()
        ])

        if valid:
            if attr_form:
                valid = valid and attr_form.is_valid()

            if user_func_form:
                valid = valid and user_func_form.is_valid()

            for i in processing_agreement_forms:
                valid = valid and i.is_valid()

        if valid:
            user = form.save(commit=False)

            if user.email == '':
                user.email = None

            if companyaddress_form.has_changed():
                user.company_address = companyaddress_form.save()
            if homeaddress_form.has_changed():
                user.home_address = homeaddress_form.save()
            if mailaddress_form.has_changed():
                user.mail_address = mailaddress_form.save()

            avatar = request.FILES.get('user-avatar', False)
            if avatar:
                file = ViewUtils.handle_uploaded_file(avatar)
                user.avatar_filename = file['file_name']
                user.avatar_base64 = file['file_base64']

            user.groups.set(groups_form.cleaned_data['groups'])
            user.save()

            if hierarchy:
                user.hierarchy.clear()
                for h in form.cleaned_data['hierarchy']:
                    UserHierarchy.objects.create(user=user, hierarchy=h)

            if user_func_form:
                user_func_form.save()

            if attr_form:
                doc_utils.save_document_attributes(user.pk, document_type.pk, attr_form.cleaned_data)

            _save_processing_agreements(processing_agreement_forms=processing_agreement_forms, user=user)

            if type:
                return redirect(type.lower() + '.list')
            else:
                return redirect('user.list')

    context = {'user': user,
               'type': type,
               'document_type': DocumentType.objects.get(code='USER'),
               'attr': attr,
               'attr_form': attr_form,
               'user_func_form': user_func_form,
               'form': form,
               'user_relation_form': user_relation_form,
               'processing_agreement_forms': processing_agreement_forms,
               'user_products': user_products,
               'user_active_products': user_active_products,
               'clients': None,
               'groups_form': groups_form,
               'companyaddress_form': companyaddress_form,
               'homeaddress_form': homeaddress_form,
               'mailaddress_form': mailaddress_form,
               'hierarchy': hierarchy,
               'mode': settings.MODE_EDIT,
               'user_upcoming_events': user_upcoming_events,
               'user_all_events': user_all_events,
               'USER_TYPE_REQUIRED_FIELDS': json.dumps(USER_TYPE_REQUIRED_FIELDS),
               'USER_TYPE_COMPANY_REQUIRED_FIELDS': json.dumps(USER_TYPE_COMPANY_REQUIRED_FIELDS),
               }
    return render(request, 'user/edit.html', context)


def view(request, id):
    user = get_object_or_404(User, pk=id)
    if hasattr(user, 'client'):
        type = 'CLIENT'
    else:
        type = None

    hierarchy = Hierarchy.objects.get(level=0, id=1).get_descendants()
    if not hierarchy:
        raise Exception(_('role.error.no_app_role'))

    if type == 'CLIENT':
        document_type = DocumentType.objects.get(code='CLIENT')
        attr_values = doc_utils.get_document_attribute_values(id=id, id_type=document_type.pk)
        attr = doc_utils.get_attributes(document_type.pk)
        attr_form = DocumentAttributeForm(data=request.POST or None, document_type=document_type, defaults=False, prefix='attribute', initial=attr_values, readonly=True)
        products = user.client.product_set.all().order_by('start_date')

    else:
        attr = None
        attr_form = None
        products = None

    events = Schedule.objects.filter(Q(host_user=user) | Q(created_by=user) | Q(invited_users=user)).order_by('-start_date')

    form = UserForm(data=request.POST or None, prefix='user', instance=user, mode=settings.MODE_VIEW, readonly=True)
    homeaddress_form = AddressForm(data=request.POST or None, instance=user.home_address, mode=settings.MODE_VIEW, prefix='homeaddress', readonly=True)
    mailaddress_form = AddressForm(data=request.POST or None, instance=user.mail_address, mode=settings.MODE_VIEW, prefix='mailaddress', readonly=True)

    groups = [i.pk for i in user.groups.all()]
    groups_form = GroupsForm(data=request.POST or None, initial=({'groups': groups}))
    groups_form.fields['groups'].choices = Group.objects.all().order_by('name').values_list('id', 'name')
    form.fields['username'].widget.attrs['readonly'] = True

    context = {'type': type,
               'attr': attr,
               'attr_form': attr_form,
               'form': form,
               'products': products,
               'groups_form': groups_form,
               'homeaddress_form': homeaddress_form,
               'mailaddress_form': mailaddress_form,
               'hierarchy': hierarchy,
               'events': events,
               'mode': settings.MODE_VIEW

               }
    return render(request, 'user/view.html', context)


class Delete(UserManagement):
    def set_mode(self):
        return settings.MODE_EDIT

    def set_app_name(self):
        self._app_name = 'document'

    def __init__(self):
        self._mode = settings.MODE_EDIT
        super(Delete, self).__init__()

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        status = 200
        response_data = {}
        id = html.mark_safe(request.POST.get('id'))
        new_adviser = Adviser.objects.get(pk=html.mark_safe(request.POST.get('newAdviser')))
        deleted_adviser = Adviser.objects.get(pk=id)

        try:
            with transaction.atomic():

                user = deleted_adviser.user
                user.is_active = False
                user.status = 'DL'
                user.save()
                deleted_adviser.broker_set.all().update(adviser=new_adviser)
                Client.objects.filter(adviser=deleted_adviser).update(adviser=new_adviser)

        except Exception as ex:
            status = 400
            response_data['errmsg'] = str(ex)

        return HttpResponse(json.dumps(response_data), status=status)


@login_required()
def id_exist(request):
    response_data = {}
    try:
        id_number = request.GET.get('id_number')

        if id_number is None:
            raise Exception('[user.id_exist]: Nie podano numeru ID')

        if py3ws_validators._validate_pesel(id_number):
            id_type = 'PESEL'
            exist = User.objects.filter(personal_id=id_number).exists()

        elif py3ws_validators._validate_nip(id_number):
            id_type = 'NIP'
            exist = User.objects.filter(nip=id_number).exists()

        elif py3ws_validators._validate_krs(id_number):
            id_type = 'KRS'
            exist = User.objects.filter(krs=id_number).exists()

        else:
            id_type = 'NONE'
            exist = 'NONE'

        response_data['status'] = 'OK'
        response_data['id_type'] = id_type
        response_data['exists'] = exist

    except Exception as e:
        response_data['status'] = 'ERROR'
        response_data['message'] = str(e)

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@login_required()
@p3permission_required('user.activate_user')
@transaction.atomic()
def active(request):
    response_data = {}
    try:
        id = request.POST.get('user[id]')
        active = request.POST.get('user[active]')

        if id is None:
            raise Exception('[user.active]: Brak parametru [ID] dla wpisu słownika')
        if active is None:
            raise Exception('[user.active]: Brak parametru [ACTIVE] dla wpisu słownika')

        user = get_object_or_404(User, pk=id)
        user.is_active = active
        user.save()

        response_data['status'] = 'OK'

    except Exception as e:
        response_data['status'] = 'ERROR'
        response_data['message'] = str(e)

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@login_required()
# @p3permission_required('user.changepassword_user')
@transaction.atomic()
def changepassword(request):
    user = request.user
    form = ChangePasswordForm(data=request.POST or None, prefix='password', user=user)
    if form.is_valid():
        user.set_password(form.cleaned_data['new_password'])
        user.initial_password = None
        user.password_valid = True
        user.save()

        return redirect('home.index')

    context = {'form': form}
    return render(request, 'user/changepassword.html', context)


@login_required()
@p3permission_required('user.resetpassword_user')
@transaction.atomic()
def reset_password(request):
    response_data = {}
    try:
        id = request.POST.get('id')
        if not id:
            raise Exception('Brak ID użytkownika')

        user = User.objects.get(pk=id)
        if user.ldap:
            raise Exception('Użytkownik LDAP nie może mieć zmienionego hasła.')
        password = user_utils.generate_password()

        user.initial_password = password
        user.set_password(password)
        user.password_valid = False
        user.save()

        response_data['status'] = 'OK'

        if user.email:
            try:
                validate_email(user.email)
                template = MessageTemplate.objects.get(code='PASSWORD_RESET')
                msg_utils.register_message(template, source={'user': user}, add_params={}, recipients=[user.email])
            except ValidationError:
                pass

    except Exception as e:
        response_data['status'] = 'ERROR'
        response_data['message'] = str(e)

    return HttpResponse(json.dumps(response_data), content_type="application/json")


def autocomplete_check(request):
    response_data = {}
    try:
        data = request.GET
        user_data = {k.replace('user-', ''): v for k, v in data.items() if k.startswith('user-')}

        q = Q()

        for k, v in user_data.items():
            if k in ['broker', 'adviser', 'hierarchy']:
                continue
            if v is not None and v != '':
                q = q & Q(**{'{0}__{1}'.format(k, 'istartswith'): v})

        users = []
        if len(q):
            user_list = User.objects.filter(q)
        else:
            user_list = None

        if user_list and user_list.count() <= 20:
            for u in User.objects.filter(q):
                users.append({'pk': u.pk,
                              'email': u.email,
                              'first_name': u.first_name,
                              'last_name': u.last_name,
                              'phone_one': u.phone_one,
                              'phone_two': u.phone_two,
                              'personal_id': u.personal_id,
                              'nip': u.nip,
                              'krs': u.krs,
                              'is_client': hasattr(u, 'client'),
                              'is_broker': hasattr(u, 'broker'),
                              'is_adviser': hasattr(u, 'adviser'),
                              'is_employee': hasattr(u, 'employee')
                              })
            response_data['too_many_users'] = False
        else:
            response_data['too_many_users'] = True

        response_data['status'] = 'OK'
        response_data['data'] = users

    except Exception as e:
        response_data['status'] = 'ERROR'
        response_data['message'] = str(e)

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@login_required()
@p3permission_required('user.list_groupuser')
def listgroup(request):
    groups = Group.objects.all().order_by('name')
    context = {'groups': groups}
    return render(request, 'user/group/list.html', context)


def _save_group_perms(group, form):
    q = []
    for i, j, k, l in settings.MODEL_PERMS_LIST:
        q += form.cleaned_data[i]

    group.permissions.set(Permission.objects.filter(pk__in=q))
    group.save()


@login_required()
@p3permission_required('user.add_groupuser')
@transaction.atomic()
def addgroup(request):
    form = GroupForm(data=request.POST or None, prefix='group')
    perm_form = PermissionForm(data=request.POST or None)

    if request.method == 'POST':

        if all([form.is_valid(), perm_form.is_valid()]):
            group = form.save()
            _save_group_perms(group, perm_form)

            # q = []
            # for i, j, k in settings.MODEL_PERMS_LIST:
            # q += perm_form.cleaned_data[i]
            #
            # group.permissions.set(Permission.objects.filter(pk__in=q))
            # group.save()
            return redirect('user.listgroup')

    context = {'form': form, 'mode': settings.MODE_CREATE, 'perm_form': perm_form}
    return render(request, 'user/group/add.html', context)


@login_required()
@p3permission_required('user.change_groupuser')
@transaction.atomic()
def editgroup(request, id):
    group_perms = {}
    group = get_object_or_404(Group, pk=id)

    for field, app_label, model, label in settings.MODEL_PERMS_LIST:
        group_perms[field] = _get_group_permissions_for_model(id, app_label, model)

    form = GroupForm(data=request.POST or None, prefix='group', instance=group)
    perm_form = PermissionForm(data=request.POST or None, initial=group_perms)

    if request.method == 'POST':
        if all([form.is_valid(), perm_form.is_valid()]):
            group = form.save()
            _save_group_perms(group, perm_form)

            # q = []
            # for i, j, k in settings.MODEL_PERMS_LIST:
            # q += perm_form.cleaned_data[i]
            #
            # group.permissions.set(Permission.objects.filter(pk__in=q))
            # group.save()

            return redirect('user.listgroup')

    context = {'form': form, 'mode': settings.MODE_CREATE, 'perm_form': perm_form}
    return render(request, 'user/group/edit.html', context)


@login_required()
@p3permission_required('user.activate_groupuser')
@transaction.atomic()
def activate_group(request):
    return HttpResponse("activate group")


@login_required()
@p3permission_required('user.anonimize')
@transaction.atomic()
@csrf_exempt
def anonimize(request):
    if not request.POST:
        raise Exception('ajax must be POST')

    response_data = {}
    status = 200

    user = User.objects.get(pk=request.POST.get('id'))
    last_name = py3ws_utils.xor_crypt_string(data=user.last_name, encode=True)

    response_data['last_name_encoded'] = last_name
    response_data['last_name_decoded'] = py3ws_utils.xor_crypt_string(last_name, encode=True)

    return HttpResponse(json.dumps(response_data), content_type="application/json", status=status)
