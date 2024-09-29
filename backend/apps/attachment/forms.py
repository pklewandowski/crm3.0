from django.utils.translation import gettext_lazy as _
from django import forms

from apps.attachment.models import Attachment
from py3ws.forms import p3form


class AttachmentForm(p3form.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AttachmentForm, self).__init__(*args, **kwargs)
        for v in self.fields:
            if v == 'description':
                continue
            self.fields[v].widget = forms.HiddenInput()
        self.fields['description'].widget = forms.Textarea(attrs={'class': 'form-control input-md attachment-description-field',
                                                                  'placeholder': 'Dodaj opis...'})

    class Meta:
        model = Attachment
        exclude = ('user', 'update_date')
