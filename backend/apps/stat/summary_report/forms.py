from django.utils.translation import gettext_lazy as _

from django import forms
from py3ws.forms import p3form

from apps.document.models import DocumentTypeStatus, DocumentType
from apps.stat.summary_report.models import StatGroupAdviser, StatGroupLoanStatus
from apps.user_func.adviser.models import Adviser
from apps.user_func.broker.models import Broker


class IncomeForm(p3form.Form):
    BUSINESS_TYPE_CHOICES = [('', 'Wszyscy'), ('B2B', 'B2B'), ('B2C', 'B2C')]
    AGREEMENT_TYPE_CHOICES = [('NEW', 'Nowa'), ('PRLG', 'Prolongata'), ('ANX', 'Aneks'), ('UGD', 'Ugoda')]
    adviser = forms.ModelMultipleChoiceField(queryset=Adviser.objects.all().order_by('user__last_name'),
                                             widget=forms.CheckboxSelectMultiple, required=False)
    broker = forms.ModelMultipleChoiceField(queryset=Broker.objects.all().order_by('user__last_name'),
                                            widget=forms.CheckboxSelectMultiple, required=False)
    status = forms.ModelMultipleChoiceField(queryset=DocumentTypeStatus.objects.filter(type=1).order_by('sq'),
                                            widget=forms.CheckboxSelectMultiple, required=False)

    business_type = forms.ChoiceField(choices=BUSINESS_TYPE_CHOICES,
                                      widget=forms.RadioSelect, required=False)
    drs = forms.ModelMultipleChoiceField(queryset=StatGroupAdviser.objects.all(),
                                         widget=forms.CheckboxSelectMultiple, required=False)
    group_status = forms.ModelMultipleChoiceField(queryset=StatGroupLoanStatus.objects.all().order_by('name'),
                                                  widget=forms.CheckboxSelectMultiple, required=False)
    agreement_type = forms.MultipleChoiceField(choices=AGREEMENT_TYPE_CHOICES,
                                               widget=forms.CheckboxSelectMultiple, required=False)
    date_from = forms.DateField(required=False)
    date_to = forms.DateField(required=False)

    class Meta:
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AdviserRankForm(p3form.Form):
    adviser = forms.ModelMultipleChoiceField(queryset=Adviser.objects.all().order_by('user__last_name'),
                                             widget=forms.CheckboxSelectMultiple, required=False)
    date_from = forms.DateField(required=False, label=_('adviser_rank.date_from'))
    date_to = forms.DateField(required=False, label=_('adviser_rank.date_to'))

    class Meta:
        fields = '__all__'


class DynamicsForm(p3form.Form):
    date_1 = forms.DateField(required=False, label=_('dynamics.date_1'))
    date_2 = forms.DateField(required=False, label=_('dynamics.date_2'))
    date_3 = forms.DateField(required=False, label=_('dynamics.date_3'))
    group_status = None

    def __init__(self):
        super().__init__()
        self.group_status = forms.ModelMultipleChoiceField(queryset=StatGroupLoanStatus.objects.all().order_by('name'),
                                                           widget=forms.CheckboxSelectMultiple, required=False)

    class Meta:
        fields = '__all__'


class StatGroupAdviserForm(p3form.ModelForm):
    adviser_list = None

    def __init__(self):
        super().__init__()
        self.adviser_list = forms.ModelMultipleChoiceField(
            queryset=Adviser.objects.all().order_by('user__last_name'),
            required=False,
            widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = StatGroupAdviser
        fields = ('name',)


class StatGroupLoanStatusForm(p3form.ModelForm):
    status_list = None

    def __init__(self):
        super().__init__()
        self.status_list = forms.ModelMultipleChoiceField(
            queryset=DocumentTypeStatus.objects.filter(type=DocumentType.objects.get(code='PZ1')).order_by('sq'),
            required=False,
            widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = StatGroupAdviser
        fields = ('name',)
