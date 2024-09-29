from django.forms import modelformset_factory
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Permission, ContentType
from py3ws.forms import p3form
from django import forms
from apps.user.models import User, UserRelation
from apps.hierarchy.models import Hierarchy
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import Group
from django.conf import settings

from . import USER_TYPE_REQUIRED_FIELDS, USER_TYPE_COMPANY_REQUIRED_FIELDS


def _get_permissions(app_label, model):
    return [(i.pk, _(f'permissions.app.{model}.{i.codename}')) for i in
            Permission.objects.filter(content_type=ContentType.objects.get(app_label=app_label, model=model)).order_by('codename')]


class UserForm(p3form.ModelForm):
    CONTRACTOR_TYPE = [
        ('CONTRACTOR', _('Partner biznesowy')),
        ('LAWOFFICE', _('Kancelaria prawna')),
        ('BAILIFF_OFFICE', _('Kancelaria komornicza'))
    ]  # todo: get from some definition, not static

    username = forms.CharField(label=_('user.username'), max_length=150, required=False)
    avatar = forms.FileField(required=False)

    hierarchy = forms.ModelMultipleChoiceField(
        queryset=Hierarchy.objects.all(),  # not optional, use .all() if unsure
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def __init__(self, *args, **kwargs):
        self.user_type = kwargs.pop('user_type', None)
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['contractor_type'].widget.choices = self.CONTRACTOR_TYPE

    def clean(self):
        cd = super(UserForm, self).clean()

        if self.user_type:
            if cd.get('is_company'):
                required = USER_TYPE_COMPANY_REQUIRED_FIELDS[self.user_type]
            else:
                required = USER_TYPE_REQUIRED_FIELDS[self.user_type]

            for i in required:
                if not cd.get(i):
                    msg = _('To pole jest wymagane')
                    self._errors[i] = self.error_class([msg])
                    if i in cd:
                        del cd[i]
        return cd

    class Meta:
        model = User
        fields = ['first_name', 'second_name', 'last_name', 'email', 'phone_one', 'phone_two',
                  'username', 'ldap', 'hierarchy', 'personal_id', 'nip', 'krs', 'avatar', 'description',
                  'is_company', 'company_name', 'company_establish_date', 'birth_date', 'representative', 'regon', 'contractor_type', 'tags']
        widgets = {
            'is_company': forms.CheckboxInput,
            'contractor_type': forms.Select
        }


class UserCompleteForm(p3form.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'second_name', 'last_name', 'email', 'phone_one', 'phone_two', 'personal_id', 'nip', 'krs']


class PermissionForm(p3form.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(PermissionForm, self).__init__(*args, **kwargs)

        for field, app_label, model, label in settings.MODEL_PERMS_LIST:
            self.fields[field] = forms.MultipleChoiceField(choices=_get_permissions(app_label, model), widget=forms.CheckboxSelectMultiple, label=label, required=False)

    class Meta:
        fields = [field for field in settings.MODEL_PERMS_LIST]


class ChangePasswordForm(p3form.Form):
    user = None
    old_password = forms.CharField(max_length=100, label=_('user.form.old_password.label'), widget=forms.PasswordInput())
    new_password = forms.CharField(max_length=100, label=_('user.form.new_password.label'), widget=forms.PasswordInput())
    confirm_password = forms.CharField(max_length=100, label=_('user.form.confirm_password.label'), widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def is_valid(self):
        valid = super(ChangePasswordForm, self).is_valid()

        # we're done now if not valid
        if not valid:
            return valid

        if not check_password(self.cleaned_data['old_password'], self.user.password):
            self.add_error('old_password', "Wprowadzone dotychczasowe hasło jest niepoprawne")
            valid = False

        if self.cleaned_data['new_password'] != self.cleaned_data['confirm_password']:
            self.add_error('confirm_password', "Pola 'Nowe hasło' oraz 'Potwierdź hasło' nie są zgodne")
            valid = False

        return valid

    class Meta:
        fields = ('old_password', 'new_password', 'confirm_password')


class GroupForm(p3form.ModelForm):
    class Meta:
        model = Group
        fields = ('name', 'description')
        labels = {'name': _('group.name'), 'description': _('group.description')}


class GroupsForm(p3form.Form):
    groups = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, label=_('user.group.form.groups.label'), required=False)

    class Meta:
        fields = ('groups',)


class UserRelationForm(p3form.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserRelationForm, self).__init__(*args, **kwargs)
        self.fields['right'].widget.attrs['data-autocomplete_url'] = '/client/get-list-for-select2/'

    class Meta:
        model = UserRelation
        fields = '__all__'


UserRelationFormset = modelformset_factory(UserRelationForm.Meta.model, form=UserRelationForm, extra=0, can_delete=True)
