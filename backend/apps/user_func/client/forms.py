from django import forms
from django.conf import settings

from apps.config.models import HoldingCompany
from apps.user_func.adviser.models import Adviser
from apps.user_func.broker.models import Broker
from apps.user_func.client import CLIENT_SOURCE
from apps.user_func.client.models import Client, ClientProcessingAgreement
from py3ws.forms import p3form
from .models import ProcessingAgreement


class ClientForm(p3form.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)
        if settings.CLIENT_HAS_BROKER:
            self.fields['adviser'].queryset = Adviser.objects.filter(user__is_active=True).order_by('user__last_name')
            self.fields['adviser'].widget.attrs['class'] = 'select2'

            self.fields['broker'].queryset = Broker.objects.filter(user__is_active=True).order_by('user__last_name')
            self.fields['broker'].widget.attrs['class'] = 'select2'

            self.fields['company'].widget.choices = [('', '----')] + [(i.pk, str(i)) for i in HoldingCompany.objects.all().order_by('-is_default', 'name')]

    class Meta:
        model = Client
        fields = ('source', 'status', 'company')
        if settings.CLIENT_HAS_BROKER:
            fields += ('broker', 'adviser')


class ClientProcessingAgreementForm1(p3form.ModelForm):
    class Meta:
        model = ClientProcessingAgreement
        exclude = ('client',)


class ClientProcessingAgreementForm(p3form.Form):
    def __init__(self, *args, **kwargs):
        super(ClientProcessingAgreementForm, self).__init__(*args, **kwargs)
        for i in ProcessingAgreement.objects.all():
            self.fields[i.pk] = forms.BooleanField(required=i.required, label=i.text, widget=forms.CheckboxInput(attrs={'value': i.pk}))


class ProcessingAgreementForm(p3form.ModelForm):
    value = forms.BooleanField(required=False,
                                   # widget=forms.Select(choices=[(None, '???'), (True, 'Tak',), (False, 'Nie')])
                                   widget=forms.NullBooleanSelect()
                                   )
    source = forms.ChoiceField(choices=[('', '----')] + CLIENT_SOURCE, required=False)

    def __init__(self, *args, **kwargs):
        super(ProcessingAgreementForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = False
        self.fields['text'].required = False

    def clean(self):
        cd = self.cleaned_data
        if cd.get('agreement_checked') and not cd.get('source'):
            msg = 'Źródło zgody musi być określone.'
            self._errors['source'] = self.error_class([msg])
            del cd['source']
        return cd

    class Meta:
        model = ProcessingAgreement
        fields = ('name', 'text')

# class ClientProcessingAgreementForm1(p3form.ModelForm):
#     processing_agreement_text = forms.CharField(widget=forms.HiddenInput)
#     processing_agreement = forms.BooleanField(required=False)
#     source = forms.ChoiceField(choices=[('', '----'),('WWW', 'WWW'), ('ADV', 'Doradca'), ('DOC', 'Oświadczenie na piśmie')], required=False)
#
#     class Meta:
#         model = ClientProcessingAgreement
#         exclude = ('client',)
