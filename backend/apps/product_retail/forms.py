from django.forms import modelformset_factory
from django.utils.translation import gettext_lazy as _
from django import forms
from py3ws.forms import p3form

from .models import ProductRetailClient, ProductRetail


class ProductRetailForm(p3form.ModelForm):
    category_name = forms.CharField(label=_('product.retail.category.name'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category_name'].widget.attrs['readonly'] = True

    class Meta:
        model = ProductRetail
        fields = '__all__'
        widgets = {
            'category': forms.HiddenInput()
        }


class ProductRetailClientForm(p3form.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductRetailClientForm, self).__init__(*args, **kwargs)

    class Meta:
        model = ProductRetailClient
        exclude = ('total_cost', 'client')
        widgets = {'payment_type': forms.Select(choices=[('CASH', 'Gotówka'), ('WALLET', 'Portfel')])}


ProductRetailClientFormset = modelformset_factory(
    ProductRetailClientForm.Meta.model,
    form=ProductRetailClientForm,
    extra=0,
    can_delete=True,
)
