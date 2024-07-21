from django.utils.translation import gettext_lazy as _
from django import forms
from py3ws.forms import p3form


class LoginForm(p3form.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(max_length=100)

    class Meta:
        fields = '__all__'
        labels = {  # 'type': _("issue.form.label.type"),
                    'username': _("login.form.label.username"),
                    'password': _("login.form.label.password"),
                    }