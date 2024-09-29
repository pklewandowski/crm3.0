from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm, TextInput
from django import forms
from .models import Agreement


class AgreementForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AgreementForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control input-sm'

    class Meta:
        model = Agreement

        fields = ['client', 'signature']
        labels = {
            "client": _("agreement.form.label.client"),
            "signature": _("agreement.form.label.signature"),
        }
        widgets = {
            'client': TextInput()
        }
