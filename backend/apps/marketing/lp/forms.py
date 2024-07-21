from py3ws.forms import p3form
from apps.marketing.lp.models import Medium, Source, LeadPage


class MediumForm(p3form.ModelForm):
    class Meta:
        model = Medium
        fields = ('name',)


class SourceForm(p3form.ModelForm):
    class Meta:
        model = Source
        fields = ('name',)


class LeadPageForm(p3form.ModelForm):
    class Meta:
        model = LeadPage
        fields = ('name',)
