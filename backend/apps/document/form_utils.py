from django import forms
from django.core.validators import RegexValidator
from django.urls import reverse

from py3ws.forms import p3form
from py3ws.utils import utils as py3ws_utils
from py3ws.forms import utils as p3ws_form_utils
from py3ws.forms.widgets.select.dataAttributesSelect import DataAttributesSelect1

from apps.attribute import NULLBOOLEAN_CHOICES
from apps.user_func.client.models import Client


class AttributeFormException(Exception):
    pass


class AttributeFormManager(p3form.Form):
    is_editable = False

    def _get_attribute_value(self, attribute):
        try:
            value = self.data['%s-%s' % (self.prefix, attribute.code)]
        except KeyError:
            value = self.initial[attribute.code] if self.initial and attribute.code in self.initial else None
        return value

    def _get_autocomplete_class(self, attribute):
        if 'autocompleteUtilsClass' not in attribute.feature:
            raise AttributeFormException("brak definicji klasy dla elementu 'autocomplete'")

        cl = py3ws_utils.get_class(attribute.feature['autocompleteUtilsClass'])
        return cl

    def _generate_table_field(self, attribute):

        self.fields[attribute.code] = forms.CharField(required=False, label='', widget=forms.HiddenInput())

    def _generate_autocomplete_field(self, attribute):

        value = self._get_attribute_value(attribute)
        cl = self._get_autocomplete_class(attribute)
        choices = []
        try:
            if value:
                choices = cl.get_for_select2(value)
        except (AttributeError, KeyError, Client.DoesNotExist):
            pass

        if self.is_editable:
            self.fields[attribute.code] = forms.CharField(required=self.required,
                                                          label=attribute.name,
                                                          widget=forms.Select(
                                                              choices=choices,
                                                              attrs={
                                                                  'class': 'autocomplete',
                                                                  'data-autocomplete_url': reverse(attribute.feature["autocomplete"])
                                                              })
                                                          )
        else:
            self.fields[attribute.code] = forms.ChoiceField(required=self.required,
                                                            label=attribute.name,
                                                            choices=choices
                                                            )

    def _generate_string_field(self, attribute):
        if attribute.lov:
            if attribute.lov['nullvalue'] and self.is_editable:
                choices = [('', '----')]
            else:
                choices = []

            lov_description = {'': ''}

            if isinstance(attribute.lov['data'], dict):
                pass
                # choices.extend([(k, v) for k, v in i.lov['data'].items()])
            else:
                for dtc in attribute.lov['data']:
                    if not self.is_editable:
                        if self.initial:
                            if (attribute.code in self.initial) and self.initial[attribute.code] == dtc['lov_value']:
                                choices.append((dtc['lov_value'], dtc['lov_label']))
                                lov_description[dtc['lov_value']] = {'name': 'description', 'value': dtc['lov_description']}
                                break
                        else:
                            break
                    else:
                        choices.append((dtc['lov_value'], dtc['lov_label']))
                        lov_description[dtc['lov_value']] = {'name': 'description',
                                                             'value': dtc['lov_description'] if 'lov_description' in dtc else ''}

            lov_description[''] = {'name': 'description', 'value': ''}

            self.fields[attribute.code] = forms.ChoiceField(choices=choices,
                                                            required=self.required,
                                                            label=attribute.name,
                                                            widget=DataAttributesSelect1(
                                                                attrs={'class': 'lov'},
                                                                choices=choices,
                                                                data=lov_description
                                                            ))
        else:
            self.fields[attribute.code] = forms.CharField(min_length=attribute.attribute.min_length,
                                                          max_length=attribute.attribute.max_length,
                                                          required=self.required,
                                                          label=attribute.name,
                                                          validators=[RegexValidator(attribute.attribute.regex,
                                                                                     message='Nieprawidłowy format. Wartość powinna być w formacie: %s'
                                                                                             % attribute.attribute.regex)])

    def _generate_text_field(self, attribute):
        self.fields[attribute.code] = forms.CharField(required=self.required,
                                                      widget=forms.Textarea(attrs={'class': 'document-attribute-textarea', 'rows': '', 'cols': ''}),
                                                      label=attribute.name)

    def _generate_decimal_field(self, attribute):
        self.fields[attribute.code] = forms.DecimalField(
            min_value=attribute.attribute.min_value,
            max_value=attribute.attribute.max_value,
            decimal_places=attribute.attribute.decimal_places,
            label=attribute.name,
            required=self.required,
            localize=True,
            widget=forms.TextInput(attrs={'localization': True})
        )

    def _generate_date_field(self, attribute):
        self.fields[attribute.code] = forms.DateField(
            required=self.required,
            label=attribute.name
        )

    def _generate_datetime_field(self, attribute):
        self.fields[attribute.code] = forms.DateTimeField(
            required=self.required,
            label=attribute.name
        )

    def _generate_dictionary_field(self, attribute):
        self.fields[attribute.code] = forms.ChoiceField(
            required=self.required,
            label=attribute.name,
            choices=p3ws_form_utils.get_dictionary_entries(attribute.dictionary.code)
        )

    def _generate_boolean_field(self, attribute):
        self.fields[attribute.code] = forms.BooleanField(
            required=self.required,
            label=attribute.name
        )

    def _generate_nullboolean_field(self, attribute):
        if not self.is_editable:
            choices = []
            if self.initial and attribute.code in self.initial:
                for k, v in NULLBOOLEAN_CHOICES:
                    if k == self.initial[attribute.code]:
                        choices = [(k, v)]
                        break
        else:
            choices = NULLBOOLEAN_CHOICES
        self.fields[attribute.code] = forms.ChoiceField(
            choices=choices,
            required=self.required,
            label=attribute.name
        )

    def _generate_hyperlink_field(self, attribute):
        self.fields[attribute.code] = forms.CharField(required=self.required,
                                                      widget=forms.TextInput(
                                                          attrs={
                                                              'class': 'hyperlink-field',
                                                              'data-type': 'hyperlink'
                                                          })
                                                      )

    def _generate_file_field(self, attribute):
        self.fields[attribute.code] = forms.CharField(required=self.required,
                                                      widget=forms.HiddenInput(
                                                          attrs={'class': 'file-upload-field',
                                                                 'data-type': 'file'
                                                                 }
                                                      ))
