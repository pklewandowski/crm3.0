from django.utils.translation import gettext_lazy as _
from django import forms
from py3ws.forms import p3form
from py3ws.forms import utils as form_utils
from .models import Attribute
from apps.document.models import DocumentTypeAttribute


class AttributeForm(p3form.ModelForm):
    generic_datatype = forms.ChoiceField(choices=form_utils.get_dictionary_entries('GENERIC_DATATYPES'), label=_('attribute.generic_datatype.label'))

    class Meta:
        model = Attribute
        fields = '__all__'
