from django.utils.translation import gettext_lazy as _
from django import forms

from apps.message.models import MessageTemplate
from py3ws.forms import p3form
from py3ws.forms import utils as form_utils


class MessageTemplateForm(p3form.ModelForm):
    type = forms.ChoiceField(choices=[('TMPL', 'Szablon'), ('INC', 'Komponent szablonu')], label=_('message.template.type'))
    def __init__(self, *args, **kwargs):
        super(MessageTemplateForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['id'] = 'ck_editor_text'
    class Meta:
        model = MessageTemplate
        fields = '__all__'

