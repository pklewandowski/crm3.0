from django.utils.translation import gettext_lazy as _
from django import forms
from py3ws.forms import p3form
from .models import ReportTemplate
import pprint


class ReportForm(p3form.ModelForm):
    template_name = forms.FileField(label=_('report.template_name'))

    class Meta:
        model = ReportTemplate
        fields = '__all__'


class ReportDatasourceForm(p3form.Form):
    report = None

    def __init__(self, *args, **kwargs):
        report = kwargs.pop('report', None)
        super(ReportDatasourceForm, self).__init__(*args, **kwargs)

        if not report:
            raise Exception('Brak obiektu raportu')

        for i in report.datasource_definition_set.all():
            if i.editable:
                if i.type == 'decimal':
                    self.fields[i.tag_name] = forms.DecimalField(required=i.required, max_digits=10, decimal_places=2, widget=forms.TextInput())
                elif i.type == 'date':
                    self.fields[i.tag_name] = forms.DateField(required=i.required)
                elif i.type == 'text':
                    self.fields[i.tag_name] = forms.CharField(required=i.required, widget=forms.TextInput)
                else:
                    self.fields[i.tag_name] = forms.CharField(required=i.required, max_length=200)
