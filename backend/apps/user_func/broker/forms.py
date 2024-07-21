from django import forms
from py3ws.forms import p3form

from apps.user_func.adviser.models import Adviser
from apps.user_func.broker.models import Broker


class BrokerForm(p3form.ModelForm):
    # broker = forms.CharField(required=False, widget=forms.Select())
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['adviser'].widget.attrs['class'] = 'select2'
        self.fields['adviser'].widget.choices = [(i.pk, str(i)) for i in Adviser.objects.filter(user__is_active=True)]

    class Meta:
        model = Broker
        fields = ('adviser',)
