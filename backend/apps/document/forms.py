from pprint import pprint

from django.utils.translation import gettext_lazy as _
from django import forms
from django.forms import formset_factory, modelformset_factory
from django.urls import reverse

from py3ws.forms import p3form
from py3ws.forms.widgets.select.dataAttributesSelect import DataAttributesSelect
from py3ws.utils import utils as py3ws_utils

from apps.attribute import NULLBOOLEAN_CHOICES
from apps.document import utils as document_utils
from apps.document.form_utils import AttributeFormManager
from apps.document.models import DocumentType, DocumentTypeSection, DocumentTypeAttribute, DocumentTypeAccountingType, \
    DocumentTypeSectionColumn, Document, DocumentTypeCategory, DocumentAttachment, DocumentScan
from apps.document.type.attribute import utils as attribute_utils
from apps.user_func.client.models import Client


class DocumentForm(p3form.ModelForm):
    status_flow = forms.ChoiceField(required=False, label=_('document.status_flow'))
    note = forms.CharField(widget=forms.Textarea(), required=False)

    def __init__(self, *args, **kwargs):

        is_owner = kwargs.pop('is_owner', None)
        is_code = kwargs.pop('is_code', None)
        is_code_editable = kwargs.pop('is_code_editable', None)
        readonly = kwargs.pop('readonly', False)
        owner_type = kwargs.pop('owner_type', None)
        available_statuses = kwargs.pop('available_statuses', None)

        super(DocumentForm, self).__init__(*args, **kwargs)

        if is_owner:
            self.fields['owner'].required = True
        if is_code:
            self.fields['code'].required = True

        if available_statuses:
            self.fields['status_flow'].choices = [(None, '-----')] + [(i.available_status.code, i.available_status.name)
                                                                      for i in available_statuses]
        if readonly:
            for k, v in self.fields.items():
                self.fields[k].widget.attrs['readonly'] = 'readonly'

    class Meta:
        model = Document
        fields = ('description', 'hierarchy', 'status', 'code', 'owner')
        widgets = {
            'hierarchy': forms.TextInput,
            'owner': forms.Select(choices=[]),
            'status': forms.TextInput(attrs={'readonly': 'readonly'})
        }


class DocumentScanForm(p3form.ModelForm):
    class Meta:
        model = DocumentScan
        fields = ('file_name', 'sq')


DocumentScanFormset = modelformset_factory(model=DocumentScanForm.Meta.model, form=DocumentScanForm, extra=0, can_delete=True)


class DocumentTypeForm(p3form.ModelForm):
    accounting_ordered = forms.CharField(max_length=200, required=False)
    accounting_unordered = forms.ModelMultipleChoiceField(queryset=DocumentTypeAccountingType.objects.filter(is_accounting_order=False), widget=forms.CheckboxSelectMultiple, required=False)
    owner_type = forms.ChoiceField(choices=[('CLIENT', 'Klient'), ('EMPLOYEE', 'Pracownik')])

    def __init__(self, *args, **kwargs):
        super(DocumentTypeForm, self).__init__(defaults=False, *args, **kwargs)
        data = {}
        choices = []
        for f in DocumentTypeCategory.objects.all():
            data[f.id] = f.attributes
            choices.append((f.id, str(f)))
        self.fields['category'].widget = DataAttributesSelect(
            choices=choices,
            data=data
        )
        self.defaults = True
        p3form.set_defaults(self)

    class Meta:
        model = DocumentType
        fields = ('category', 'name', 'code', 'owner_type', 'editable', 'is_schedule')


class DocumentTypeSectionForm(p3form.ModelForm):
    class Meta:
        model = DocumentTypeSection
        exclude = ('document_type', 'sq', 'parent')
        widgets = {'view_type': forms.Select(choices=[('BLOCK', 'blok'), ('TABLE', 'tabela')])}


class DocumentTypeSectionColumnForm(p3form.ModelForm):
    class Meta:
        model = DocumentTypeSectionColumn
        exclude = ('sq', 'section')


class DocumentTypeAttributeForm(p3form.ModelForm):
    section_column = forms.ModelChoiceField(required=True, label=_('document.type.attribute.section.column'),
                                            queryset=DocumentTypeSectionColumn.objects.none(),
                                            empty_label=None)
    null_value = forms.BooleanField(required=False, label=_('document.type.attribute.null_value'))

    class Meta:
        model = DocumentTypeAttribute
        fields = ('name', 'section_column', 'null_value', 'attribute')


class DocumentAttachmentForm(p3form.ModelForm):
    class Meta:
        model = DocumentAttachment
        fields = ('document', 'attachment')


class DocumentAttributeLovForm(p3form.Form):
    lov_value = forms.CharField(required=True)
    lov_label = forms.CharField(required=True)
    lov_description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'textarea-small'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.initial:
            self.fields['lov_value'].widget.attrs['readonly'] = 'readonly'

    class Meta:
        fields = '__all__'


class DocumentAttributeForm(AttributeFormManager):
    attributes = None
    attribute_features = None
    empty_permitted = None
    section = None
    user = None
    hierarchy = set()

    def __init__(self, *args, **kwargs):

        self.attributes = kwargs.pop('attributes', {})
        self.attribute_features = kwargs.pop('attribute_features', {})
        self.empty_permitted = kwargs.pop('empty', True)
        self.section = kwargs.pop('section', False)
        self.user = kwargs.pop('user', None)
        self.status_flow = kwargs.pop('status_flow', None)
        # TODO: docelowo zmienić - np. pobierać z sesji, bo teraz za każdym razem musi wykonać kweerendę do bazy - to dla id=1 (pozyczka) wychodzi kilkanaście razy
        if self.user:
            self.hierarchy = set([i.pk for i in self.user.hierarchy.all()])
        else:
            self.hierarchy = set()
        # self.readonly = kwargs.pop('readonly', False)

        status = kwargs.pop('status', None)
        table = kwargs.pop('table', None)

        document_type = kwargs.pop('document_type', None)

        super().__init__(*args, **kwargs)

        if document_type is not None:
            # if status is None:
            #     self.status = document_utils.get_initial_status(document_type)

            for key, i in self.attributes.items():
                if not self.attribute_features[i.pk]['visible']:
                    continue

                if not self.status_flow:
                    self.required = False
                    add_required_class = self.attribute_features[i.pk]['required']
                else:
                    self.required = self.attribute_features[i.pk]['required']
                    add_required_class = False

                self.is_editable = self.attribute_features[i.pk]['editable']  # not self.readonly and

                if self.is_editable and i.hierarchy:
                    if not (self.hierarchy & set(i.hierarchy)):
                        self.is_editable = False

                if i.is_table:
                    self._generate_table_field(i)

                if i.feature and 'autocomplete' in i.feature.keys():
                    self._generate_autocomplete_field(i)

                elif i.attribute.generic_datatype == 'string':
                    self._generate_string_field(i)

                elif i.attribute.generic_datatype == 'text':
                    self._generate_text_field(i)

                elif i.attribute.generic_datatype == 'decimal':
                    self._generate_decimal_field(i)

                elif i.attribute.generic_datatype == 'date':
                    self._generate_date_field(i)

                elif i.attribute.generic_datatype == 'datetime':
                    self._generate_datetime_field(i)

                elif i.attribute.generic_datatype == 'dictionary' and i.dictionary:
                    self._generate_dictionary_field(i)

                elif i.attribute.generic_datatype == 'boolean':
                    self.fields[i.code] = forms.BooleanField(required=self.required, label=i.name)

                elif i.attribute.generic_datatype == 'nullboolean':
                    self._generate_nullboolean_field(i)

                elif i.attribute.generic_datatype == 'hyperlink':
                    self._generate_hyperlink_field(i)

                elif i.attribute.generic_datatype == 'file':
                    self._generate_file_field(i)

                if not self.is_editable:
                    if type(self.fields[i.code]) == forms.BooleanField:
                        self.fields[i.code].widget.attrs['disabled'] = 'disabled'
                    else:
                        self.fields[i.code].widget.attrs['readonly'] = 'readonly'

                if i.dependency:
                    self.fields[i.code].widget.attrs = py3ws_utils.merge_two_dicts(self.fields[i.code].widget.attrs, {'data-dependency': i.dependency})

                if i.css_class:
                    if 'class' in self.fields[i.code].widget.attrs:
                        self.fields[i.code].widget.attrs['class'] = self.fields[i.code].widget.attrs['class'] + ' ' + i.css_class
                    else:
                        self.fields[i.code].widget.attrs['class'] = i.css_class

                if add_required_class:
                    self.fields[i.code].label_classes = (self.required_css_class,)
                    self.fields[i.code].widget.attrs['label_classes'] = (self.required_css_class,)

                self.fields[i.code].widget.attrs = py3ws_utils.merge_two_dicts(self.fields[i.code].widget.attrs, {'data-id': i.pk})

            # przechowywane row_uid dla grupy powtarzalnych subsekcji
            self.fields['row_uid'] = forms.CharField(required=False, widget=forms.HiddenInput())
            if table:
                self.fields['parent_row_uid'] = forms.CharField(required=False, widget=forms.HiddenInput())

        self.defaults = True
        self.set_defaults()

    def clean(self):
        cd = self.cleaned_data
        for key, i in self.attributes.items():
            if not self.attribute_features[key]['required']:
                continue
            if i.dependency:
                master_id = list(i.dependency.keys())[0]
                master_value = cd.get(self.attributes[int(master_id)].code)
                dependency_values = i.dependency[master_id]
                if master_value not in dependency_values:
                    try:
                        del self._errors[i.code]
                    except KeyError:
                        pass
        return cd

    class Meta:
        fields = '__all__'


class DocumentTypeAttributeFeatureForm(p3form.Form):
    def __init__(self, *args, **kwargs):
        self.document_type = kwargs.pop('document_type', None)
        self.attributes = kwargs.pop('attributes', None)
        self.statuses = kwargs.pop('statuses', None)
        self.sections = kwargs.pop('sections', None)
        self.feature = ('V', 'E', 'R')
        super(DocumentTypeAttributeFeatureForm, self).__init__(*args, **kwargs)

        if self.document_type is not None:
            for j in self.statuses:
                for idx, a in enumerate(self.attributes):
                    for i in a:
                        for f in self.feature:  # [V]isible, [E]ditable, [R]equired
                            name = attribute_utils.get_field_name(attribute=i, status_code=j.code, section=self.sections[idx], feature=f)
                            self.fields[name] = forms.BooleanField(required=False, label=i.name,
                                                                   widget=forms.CheckboxInput(
                                                                       attrs={
                                                                           'data-section': self.sections[idx].pk,  # str(i.section.pk),
                                                                           'data-status': j.code,
                                                                           'data-feature': f
                                                                       }))

                for s in self.sections:
                    for f in self.feature:
                        self.fields["%s_%s_%s" % (str(s.pk), j.code, f)] = forms.BooleanField(required=False,
                                                                                              widget=forms.CheckboxInput(
                                                                                                  attrs={
                                                                                                      'class': 'select-all',
                                                                                                      'data-section': str(s.pk),
                                                                                                      'data-status': j.code,
                                                                                                      'data-feature': f
                                                                                                  }))

    class Meta:
        fields = '__all__'


def get_document_attribute_form(data,
                                document_type,
                                initial,
                                attributes=None,
                                attribute_features=None,
                                document_status=None,
                                document_status_flow=None,
                                document=None,
                                prefix=None,
                                readonly=False,
                                form_name=None,
                                user=None):
    initial = initial or (document_utils.get_document_attribute_values(document.pk, id_type=document_type.pk) if document else None)
    return DocumentAttributeForm(data=data,
                                 initial=initial,
                                 status=document_status,
                                 status_flow=document_status_flow,
                                 document_type=document_type,
                                 attributes=attributes,
                                 attribute_features=attribute_features,
                                 readonly=readonly,
                                 defaults=False,
                                 prefix=prefix,
                                 form_name=form_name,
                                 user=user)


LovFormset = formset_factory(form=DocumentAttributeLovForm, extra=0, can_delete=True)
AttributeFormset = formset_factory(form=DocumentAttributeForm, extra=0, can_delete=True)

DocumentTypeSectionColumnFormset = modelformset_factory(DocumentTypeSectionColumnForm.Meta.model,
                                                        form=DocumentTypeSectionColumnForm,
                                                        extra=0,
                                                        can_delete=True
                                                        )
