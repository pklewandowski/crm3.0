from django.utils.translation import gettext_lazy as _
from django import forms
from django.conf import settings
from py3ws.utils import utils
from py3ws.forms import fields
from py3ws.decorators.decorators import static_var


# @static_var("h", "[")
def get_dictionary_hierarchy(entry):
    h = '{"id":"%s", "text":"%s"' % (entry.pk, entry.label)
    if entry.children_set.all():
        h += ', "icon":"jstree-folder", "li_attr" : { "class" : "hierarchy-tree-no-checkbox" },  "children":['
        for c in entry.children_set.all():
            h += get_dictionary_hierarchy(c)
        h = h[0: len(h) - 1] + ']'
    else:
        h += ', "icon":"jstree-file"'
    return h + "},"


def get_dictionary_entries(dictname, value='value', label='label', hierarchy=False):
    dict_class = settings.DICTIONARY_CLASS
    if not dict_class:
        raise Exception('brak definicji klasy słownika')
    cl = utils.myimport(dict_class)
    if not hierarchy:
        return [(None, '-------')] + [(i, j) for i, j in cl.objects.filter(dictionary__code=dictname, active=True).order_by('sq').values_list(value, label)]
    else:
        h = '['
        for entry in cl.objects.filter(dictionary__code=dictname, active=True, parent=None).order_by('sq'):
            h += get_dictionary_hierarchy(entry)

        h = h[0: len(h) - 1] + ']'
        return h


def set_defaults(frm):
    try:
        if not frm.defaults:
            return
    except AttributeError as e:
        pass

    frm.error_css_class = settings.FORM_FIELD_ERROR_CSS_CLASS or 'form-field-error'
    frm.required_css_class = settings.FORM_FIELD_REQUIRED_CSS_CLASS or 'form-field-required'

    for visible in frm.visible_fields():
        visible.field.widget.attrs['autocomplete'] = 'off'
        visible.field.widget.attrs['data-code'] = visible.name

        if visible.field.widget.__class__.__name__ not in ['CheckboxSelectMultiple', 'RadioSelect'] and \
            visible.field.__class__.__name__ not in ['BooleanField']:
            if 'class' not in visible.field.widget.attrs:
                visible.field.widget.attrs['class'] = frm.field_base_class  # settings.FORM_FIELD_BASE_CSS_CLASS or 'form-control input-sm'
            else:
                visible.field.widget.attrs['class'] += ' %s' % frm.field_base_class  # (settings.FORM_FIELD_BASE_CSS_CLASS or 'form-control input-sm')
        else:
            visible.field.widget.attrs['class'] = ''

        if frm.readonly:
            visible.field.widget.attrs['readonly'] = True

        # if isinstance(visible.field, forms.DateTimeField) or isinstance(visible.field, forms.DateField):
        c = ''
        if isinstance(visible.field, forms.DateTimeField):
            c = ' datetime-field'
        if isinstance(visible.field, fields.CalendarDateTimeField):
            c = ' calendar-datetime-field'
        elif isinstance(visible.field, forms.DateField):
            c = ' date-field'
        elif isinstance(visible.field, forms.TimeField):
            c = ' time-field'

        visible.field.widget.attrs['class'] += c

    try:
        if frm.mode == settings.MODE_FILTER:
            frm.fields['p3_sort_field'] = forms.CharField(required=False, widget=forms.HiddenInput(attrs={'id': 'p3_sort_field'}))
            frm.fields['p3_sort_dir'] = forms.CharField(required=False, widget=forms.HiddenInput(attrs={'id': 'p3_sort_dir'}))
            frm.fields['p3_mode'] = forms.CharField(required=False, widget=forms.HiddenInput(attrs={'id': 'p3_mode'}))
            frm.fields['p3_csv'] = forms.CharField(required=False, widget=forms.HiddenInput(attrs={'id': 'p3_csv'}))
    except AttributeError:
        pass

    if hasattr(frm, 'exclude_list'):
        for f in frm.exclude_list:
            del frm.fields[f]


class GenericForm(forms.Form):
    error_css_class = settings.FORM_FIELD_ERROR_CSS_CLASS or 'form-field-error'
    required_css_class = settings.FORM_FIELD_REQUIRED_CSS_CLASS or 'form-field-required'

    def set_defaults(self):
        set_defaults(self)

    def __init__(self, *args, **kwargs):
        self.exclude_list = kwargs.pop('exclude_list', '')
        self.readonly = kwargs.pop('readonly', False)
        self.hidden = kwargs.pop('hidden', False)
        self.mode = kwargs.pop('mode', None)
        self.defaults = kwargs.pop('defaults', True)
        super(GenericForm, self).__init__(*args, **kwargs)
        if self.defaults:
            set_defaults(self)


class Form(forms.Form):
    error_css_class = settings.FORM_FIELD_ERROR_CSS_CLASS or 'form-field-error'
    required_css_class = settings.FORM_FIELD_REQUIRED_CSS_CLASS or 'form-field-required'
    form_name = ''

    def set_defaults(self):
        set_defaults(self)

    def __init__(self, *args, **kwargs):
        self.form_name = kwargs.pop('form_name', None)
        self.readonly = kwargs.pop('readonly', False)
        self.hidden = kwargs.pop('hidden', False)
        self.mode = kwargs.pop('mode', '')
        self.defaults = kwargs.pop('defaults', True)
        self.field_base_class = kwargs.pop('field_base_class', (settings.FORM_FIELD_BASE_CSS_CLASS or 'form-control input-sm'))
        super(Form, self).__init__(*args, **kwargs)

        if self.defaults:
            set_defaults(self)


class ModelForm(forms.ModelForm):
    error_css_class = settings.FORM_FIELD_ERROR_CSS_CLASS or 'form-field-error'
    required_css_class = settings.FORM_FIELD_REQUIRED_CSS_CLASS or 'form-field-required'
    form_name = ''

    def __init__(self, *args, **kwargs):
        self.form_name = kwargs.pop('form_name', None)
        self.exclude_list = kwargs.pop('exclude_list', '')
        self.mode = kwargs.pop('mode', '')
        self.defaults = kwargs.pop('defaults', True)
        self.readonly = kwargs.pop('readonly', False)
        self.hidden = kwargs.pop('hidden', False)
        self.field_base_class = kwargs.pop('field_base_class', settings.FORM_FIELD_BASE_CSS_CLASS or 'form-control input-sm')

        super(ModelForm, self).__init__(*args, **kwargs)
        set_defaults(self)


class FilterForm(GenericForm):
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Wpisz frazę wyszukiwania...'}))
    page = forms.CharField(max_length=10, required=False, widget=forms.HiddenInput())
    page_result = forms.ChoiceField(required=False, choices=[(10, 10), (20, 20), (30, 30)])

    def __init__(self, *args, **kwargs):
        self.mode = settings.MODE_FILTER
        self.field_base_class = kwargs.pop('field_base_class', (settings.FORM_FIELD_BASE_CSS_CLASS or 'form-control input-sm'))
        super(FilterForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = '__all__'
