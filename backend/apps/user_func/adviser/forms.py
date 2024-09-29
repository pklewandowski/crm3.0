from django import forms
from py3ws.forms import p3form
from apps.user_func.adviser.models import Adviser


class AdviserForm(p3form.ModelForm):
    dummy = forms.BooleanField(required=False)

    class Meta:
        model = Adviser
        fields = ('dummy',)
