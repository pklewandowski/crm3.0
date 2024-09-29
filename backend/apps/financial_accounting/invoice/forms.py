from django.utils.translation import gettext_lazy as _

from apps.hierarchy.models import Hierarchy
from py3ws.forms import p3form
from py3ws.forms import utils as form_utils
from .models import Invoice, InvoiceItem, InvoiceExtraItem
from django import forms


class InvoiceForm(p3form.ModelForm):
    class Meta:
        model = Invoice
        exclude = ('document', 'type', 'attachments',)


class InvoiceItemForm(p3form.ModelForm):

    class Meta:
        vat_tax_list = [(23, '23%'),
                        (8, '8%'),
                        (7, '7%'),
                        (4, '4%')
                        ]
        model = InvoiceItem
        fields = '__all__'
        widgets = {
            'name': forms.Textarea(attrs={'rows': 1}),
            'quantity': forms.TextInput,
            'unit_price': forms.TextInput,
            'unit_of_measure': forms.TextInput,
            'net_value': forms.TextInput,
            'tax_value': forms.Select(choices=vat_tax_list)
        }


class InvoiceExtraItemForm(p3form.ModelForm):
    class Meta:
        model = InvoiceExtraItem
        fields = '__all__'
        widgets = {
            'name': forms.Select(choices=form_utils.get_dictionary_entries('INVOICE_EXTRA_ITEMS'))
        }
