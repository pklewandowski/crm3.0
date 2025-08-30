from django import forms
from django.forms import modelformset_factory, BaseModelFormSet
from django.utils.translation import gettext_lazy as _

from apps.document.models import DocumentType, DocumentTypeSection, DocumentTypeAttribute
from py3ws.forms import p3form
from .api.instalment_schedule import INSTALMENT_MATURITY_DATE_SELECTOR, INSTALMENT_CAPITAL_SELECTOR, \
    INSTALMENT_COMMISSION_SELECTOR, INSTALMENT_INTEREST_SELECTOR, INSTALMENT_TOTAL_SELECTOR
from .models import Product, ProductSchedule, ProductCashFlow, ProductAction, ProductClient, \
    ProductCommission, ProductTypeCommission, ProductInterestGlobal, ProductTranche
from ..hierarchy.models import Hierarchy


class ProductTypeForm(p3form.ModelForm):
    class Meta:
        model = DocumentType
        fields = '__all__'


class ProductTypeSectionForm(p3form.ModelForm):
    class Meta:
        model = DocumentTypeSection
        exclude = ('product_type', 'sq')


class ProductTypeAttributeForm(p3form.ModelForm):
    class Meta:
        model = DocumentTypeAttribute
        exclude = ('product_type', 'sq')


class ProductScheduleForm(p3form.ModelForm):
    instalment_total = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[
            'instalment_total'].initial = self.instance.instalment_capital + self.instance.instalment_commission + self.instance.instalment_interest
        self.fields['instalment_interest'].widget.attrs['readonly'] = 'readonly'
        self.fields['instalment_capital'].widget.attrs['readonly'] = 'readonly'
        self.fields['instalment_interest'].widget.attrs['readonly'] = 'readonly'
        self.fields['instalment_commission'].widget.attrs['readonly'] = 'readonly'
        # self.fields['instalment_total'].widget.attrs['readonly'] = 'readonly'

        # todo: bypass until date-calendar will be unified in whole project to vanillajs-calendar-3ws control
        self.fields['maturity_date'].widget.attrs['class'] = self.fields['maturity_date'].widget.attrs['class'].replace(
            'date-field', 'vanilla-date-field')

        self.fields['maturity_date'].widget.attrs['class'] += f' {INSTALMENT_MATURITY_DATE_SELECTOR}'
        self.fields['instalment_capital'].widget.attrs['class'] += f' {INSTALMENT_CAPITAL_SELECTOR}'
        self.fields['instalment_commission'].widget.attrs['class'] += f' {INSTALMENT_COMMISSION_SELECTOR}'
        self.fields['instalment_interest'].widget.attrs['class'] += f' {INSTALMENT_INTEREST_SELECTOR}'
        self.fields['instalment_total'].widget.attrs['class'] += f' {INSTALMENT_TOTAL_SELECTOR}'

    def clean(self):
        cd = super().clean()

    class Meta:
        model = ProductSchedule
        fields = '__all__'
        localized_fields = ('instalment_capital', 'instalment_commission', 'instalment_interest')

        widgets = {
            'total': forms.TextInput,
            'maturity_date': forms.TextInput,
            'instalment_capital': forms.TextInput,
            'instalment_interest': forms.TextInput,
            'instalment_commission': forms.TextInput,
        }


class ProductForm(p3form.ModelForm):
    accounting_ordered = forms.CharField(max_length=200, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['agreement_no'].widget.attrs['readonly'] = 'readonly'
        self.fields['value'].widget.attrs['readonly'] = 'readonly'
        self.fields['start_date'].widget.attrs['readonly'] = 'readonly'
        self.fields['start_date'].localize = False

        # todo: bypass until date-calendar will be unified in whole project to vanillajs-calendar-3ws control
        self.fields['start_date'].widget.attrs['class'] = self.fields['start_date'].widget.attrs['class'].replace(
            'date-field', 'vanilla-date-field')
        self.fields['end_date'].widget.attrs['class'] = self.fields['end_date'].widget.attrs['class'].replace(
            'date-field', 'vanilla-date-field')
        self.fields['capitalization_date'].widget.attrs['class'] = self.fields['capitalization_date'].widget.attrs[
            'class'].replace('date-field', 'vanilla-date-field')
        self.fields['termination_date'].widget.attrs['class'] = self.fields['capitalization_date'].widget.attrs[
            'class'].replace('date-field', 'vanilla-date-field')

    class Meta:
        model = Product
        fields = (
            'agreement_no',
            'value',
            # 'creditor',
            'start_date',
            'end_date',
            'termination_date',
            'capitalization_date',
            'accounting_ordered',
            'client'
        )
        localized_fields = ('value',)
        widgets = {
            'start_date': forms.TextInput,
            'end_date': forms.TextInput,
            'termination_date': forms.TextInput,
            'capitalization_date': forms.TextInput,
            'value': forms.TextInput,
            'client': forms.HiddenInput,
        }


class ProductClientForm(p3form.ModelForm):
    class Meta:
        model = ProductClient
        fields = '__all__'
        widgets = {'client': forms.TextInput}


class ProductAttributeForm(p3form.Form):
    def __init__(self, *args, **kwargs):

        type = kwargs.pop('type', None)

        super(ProductAttributeForm, self).__init__(*args, **kwargs)

        if type is not None:
            attr = DocumentTypeAttribute.objects.filter(document_type=type).order_by('sq')

            for i in attr:
                if i.generic_datatype == 'string':
                    self.fields[i.name] = forms.CharField(max_length=i.data_type.max_length, required=i.is_required)
                elif i.data_type.generic_datatype == 'text':
                    self.fields[i.name] = forms.CharField(required=i.is_required, widget=forms.Textarea())
                elif i.data_type.generic_datatype == 'decimal':
                    self.fields[i.name] = forms.DecimalField(max_digits=i.data_type.max_length,
                                                             decimal_places=i.data_type.decimal_places,
                                                             required=i.is_required, widget=forms.TextInput)
                elif i.data_type.generic_datatype == 'date':
                    self.fields[i.name] = forms.DateField(required=i.is_required)
                elif i.data_type.generic_datatype == 'datetime':
                    self.fields[i.name] = forms.DateTimeField(required=i.is_required)
                # elif i.data_type.generic_datatype == 'dictionary':
                #     self.fields[i.name] = forms.ChoiceField(required=i.is_required, choices=form_utils.get_dictionary_entries(i.data_type.dictionary.code))

        self.set_defaults()

    class Meta:
        fields = '__all__'


class ProductCashFlowForm(p3form.ModelForm):
    subtype = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(ProductCashFlowForm, self).__init__(*args, **kwargs)

        if not self.instance.editable:
            for i in self.fields:
                self.fields[i].widget.attrs['readonly'] = True

        # todo: bypass until date-calendar will be unified in whole project to vanillajs-datepicker-3ws control
        self.fields['cash_flow_date'].widget.attrs['class'] = self.fields['cash_flow_date'].widget.attrs[
            'class'].replace('date-field', 'vanilla-date-field')

        self.fields['cash_flow_date'].localize = False

        self.fields['accounting_date'].widget.attrs['class'] = self.fields['accounting_date'].widget.attrs[
            'class'].replace('date-field', 'vanilla-date-field')

        self.fields['accounting_date'].localize = False

    def clean(self):
        cd = super().clean()

        if cd.get('type').code != 'COST' and cd.get('cash_flow_date') is None:
            self._errors['cash_flow_date'] = self.error_class(['Dla wpłat i umorzeń pole jest wymagane.'])
            del cd['cash_flow_date']

        elif cd.get('cash_flow_date') is None and cd.get('accounting_date') is None:
            self._errors['cash_flow_date'] = self.error_class(
                ['Jedna z dat (data rozliczenia lub data księgowania) jest wymagana.'])

            self._errors['accounting_date'] = self.error_class(
                ['Jedna z dat (data rozliczenia lub data księgowania) jest wymagana.'])

            del cd['cash_flow_date']
            del cd['accounting_date']

    class Meta:
        model = ProductCashFlow
        fields = (
            'cash_flow_date',
            'accounting_date',
            'description',
            'type',
            'subtype',
            'value',
            'product',
            'id',
            'entry_source',
            'editable'
        )
        # localized_fields = ('value',)
        widgets = {
            'cash_flow_date': forms.TextInput,  # todo: this line made date unlocalized. Find out why
            'accounting_date': forms.TextInput,  # todo: this line made date unlocalized. Find out why
            'type': forms.TextInput,
            'value': forms.TextInput,
            'subtype': forms.Select
        }


# class ProductInterestForm(p3form.ModelForm):
#     statutory_rate = PercentageField()
#     delay_rate = PercentageField()
#     delay_max_rate = PercentageField()
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         if self.instance.is_set_globally:
#             for i in self.fields:
#                 self.fields[i].widget.attrs['readonly'] = True
#             self.fields['type'].choices = [(self.instance.type.pk, self.instance.type.name)]
#
#         # todo: bypass until date-calendar will be unified in whole project to vanillajs-datepicker-3ws control
#         self.fields['start_date'].widget.attrs['class'] = self.fields['start_date'].widget.attrs['class'].replace('date-field', 'vanilla-date-field')
#         #
#         self.fields['start_date'].widget.attrs['data-code'] = "interest_start_date"
#         self.fields['statutory_rate'].widget.attrs['data-code'] = "interest_statutory_rate"
#
#     class Meta:
#         model = ProductInterest
#         exclude = ('is_set_globally',)
#         localized_fields = ('statutory_rate', 'delay_rate', 'delay_max_rate')
#         widgets = {
#             # 'value': forms.TextInput,
#             'statutory_rate': forms.TextInput,
#             'start_date': forms.TextInput,
#         }


class ProductScheduleFeatureForm(p3form.Form):
    nominal_instalment_value = forms.DecimalField(max_digits=10, decimal_places=2, required=True,
                                                  widget=forms.TextInput,
                                                  label=_('product.schedule.feature.nominal_instalment_value'))
    nominal_instalment_number = forms.IntegerField(required=True, widget=forms.TextInput,
                                                   label=_('product.schedule.feature.nominal_instalment_number'))

    def __init__(self, *args, **kwargs):
        super(ProductScheduleFeatureForm, self).__init__(*args, **kwargs)
        self.set_defaults()

    class Meta:
        fields = '__all__'


class ProductInterestFeatureForm(p3form.Form):
    interest_percentage = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.TextInput, required=True,
                                             label=_('product.interest.feature.interest_percentage'))
    interest_type = forms.ChoiceField(required=True, label=_('product.interest.feature.interest_type'))

    def __init__(self, *args, **kwargs):
        super(ProductInterestFeatureForm, self).__init__(*args, **kwargs)
        self.set_defaults()

    class Meta:
        fields = '__all__'


class ProductActionForm(p3form.ModelForm):
    class Meta:
        model = ProductAction
        exclude = ('attachments', 'action_date', 'product', 'created_by', 'report')
        widgets = {'description': forms.Textarea, 'cost': forms.TextInput}


class TestCopyPasteForm(forms.Form):
    image_data = forms.CharField(widget=forms.HiddenInput, max_length=None)

    class Meta:
        fields = '__all__'


class ProductTypeCommissionForm(p3form.ModelForm):
    commission_type_choices = [
        ('PRC', 'procentowa'),
        ('CSH', 'kwotowa')
    ]
    commission_period_choices = [
        ('IN', 'na wejście'),
        ('OUT', 'na wyjście'),
        ('MC', 'miesięczna'),
        ('QR', 'kwartalna'),
        ('YR', 'roczna'),
    ]

    # if type == PRC => liczona od:  [
    #                 - saldo na dany dzień => DAY_BALANCE (PRC)
    #                 - średnia arytmetyczna od zaangażowanego kapitału na dany okres określony w period => [MC, QR, YR] CAPITAL_INVOLVED_AVG (PRC)
    #                 - od niewykorzystanego / potencjalnego salda - za gotowość okres określony w period => [MC, QR, YR] CAPITAL_UNUSED (PRC)
    #            ]
    # if typ == CSH => KWOTOWA - commission_calculation_type_choices NIE DOTYCZY
    commission_calculation_type_choices = [
        ('', '------'),
        ('LIMIT', 'od wartości pożyczki (limit)'),
        ('DAY_BALANCE', 'saldo na dzień'),
        ('CAPITAL_INVOLVED_AVG', 'średnia arytmetyczna od zaangażowanego kapitału'),
        ('CAPITAL_UNUSED', 'niewykorzystany kapitał')
    ]

    type = forms.ChoiceField(choices=commission_type_choices, label=_('product.type.commission.type'))
    period = forms.ChoiceField(choices=commission_period_choices, label=_('product.type.commission.period'))
    calculation_type = forms.ChoiceField(choices=commission_calculation_type_choices,
                                         label=_('product.type.commission.calculation_type'))

    class Meta:
        model = ProductTypeCommission
        exclude = ('document_type',)


class ProductCommissionForm(p3form.ModelForm):
    class Meta:
        model = ProductCommission
        fields = '__all__'
        # widgets = {'description': forms.TextInput}


class ProductInterestGlobalForm(p3form.ModelForm):
    class Meta:
        model = ProductInterestGlobal
        exclude = ('creation_date', 'created_by', 'type')
        widgets = {'value': forms.TextInput, 'value_overdue': forms.TextInput}


class ProductTrancheForm(p3form.ModelForm):
    lender = forms.ModelChoiceField(
        queryset=Hierarchy.objects.filter(type='CMP').order_by('name'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label=None
    )

    def __init__(self, *args, **kwargs):
        super(ProductTrancheForm, self).__init__(*args, **kwargs)
        self.fields['launch_date'].widget.attrs['class'] = self.fields['launch_date'].widget.attrs[
            'class'].replace('date-field', 'vanilla-date-field')
        self.fields['launch_date'].localize = False

    class Meta:
        model = ProductTranche
        fields = 'product', 'launch_date', 'title', 'value', 'lender'
        widgets = {
            'launch_date': forms.TextInput,
            'value': forms.TextInput,
        }


class ProductTrancheBaseFormset(BaseModelFormSet):
    def clean(self):
        if any(self.errors):
            return

        dt = self.forms[0].cleaned_data['launch_date']
        product = self.forms[0].cleaned_data['product']

        if not dt:
            raise forms.ValidationError("First tranche has to have launch data filled")

        total_tranche_value = self.forms[0].cleaned_data['value']

        for form in self.forms[1:]:
            if form.cleaned_data['launch_date'] and form.cleaned_data['launch_date'] < dt:
                form.add_error('launch_date', 'Tranche date cannot be older the first tranche')
                # raise forms.ValidationError('Tranche date cannot be older then the first tranche date')

            if not form.cleaned_data.get('DELETE'):
                total_tranche_value += form.cleaned_data['value']

        if total_tranche_value > product.value:
            raise forms.ValidationError(
                f"Sum of product tranches: {total_tranche_value} "
                f"cannot exceed product value: {product.value} "
            )


ClientFormset = modelformset_factory(ProductClientForm.Meta.model, form=ProductClientForm, extra=0, can_delete=True)
ScheduleFormset = modelformset_factory(ProductScheduleForm.Meta.model, form=ProductScheduleForm, extra=0,
                                       can_delete=True)

CashFlowFormset = modelformset_factory(ProductCashFlowForm.Meta.model, form=ProductCashFlowForm, extra=0,
                                       can_delete=True)

CommissionFormset = modelformset_factory(ProductCommissionForm.Meta.model, form=ProductCommissionForm, extra=0,
                                         can_delete=True)

ProductTrancheFormset = modelformset_factory(ProductTrancheForm.Meta.model,
                                             form=ProductTrancheForm,
                                             formset=ProductTrancheBaseFormset,
                                             extra=0,
                                             can_delete=True)
