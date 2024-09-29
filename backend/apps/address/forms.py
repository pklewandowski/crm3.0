from django.utils.translation import gettext_lazy as _
from django import forms
from django.forms import ModelForm
from .models import Address, AddressStreetPrefix
from py3ws.forms import p3form

class AddressForm(p3form.ModelForm):
    # choices = []
    # for i in AddressStreetPrefix.objects.all():
    # choices.append((i.id, i.code))
    street_prefix = forms.ModelChoiceField(queryset=AddressStreetPrefix.objects.all(), widget=forms.Select, required=False)  # .CharField(widget=forms.Select(choices=choices))

    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)


    class Meta:
        model = Address
        fields = ['type', 'street_prefix', 'street', 'street_no', 'apartment_no', 'post_code', 'city', 'province',
                  'country', 'email', 'phone']
        labels = {'street_prefix': _('address.form.street_prefix.label'),
                  'street': _('address.form.street.label'),
                  'street_no': _('address.form.street_no.label'),
                  'apartment_no': _('address.form.apartment_no.label'),
                  'post_code': _('address.form.post_code.label'),
                  'city': _('address.form.city.label'),
                  'province': _('address.form.province.label'),
                  'country': _('address.form.country.label'),
                  'email': _('address.form.email.label'),
                  'phone': _('address.form.phone.label')
                  }
