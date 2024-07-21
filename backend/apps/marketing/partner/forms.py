from django import forms
from django.forms import formset_factory, modelformset_factory
from py3ws.forms import p3form

from apps.marketing.partner.models import PartnerLead, PartnerAgreement, PartnerLeadAgreement, PartnerSecurityType


class PartnerLeadForm(p3form.ModelForm):
    class Meta:
        model = PartnerLead
        exclude = ('creation_date', 'agreements')


class PartnerLeadAgreementForm(p3form.ModelForm):
    class Meta:
        model = PartnerLeadAgreement
        fields = ('is_checked', 'agreement')


PartnerAgreementFormset = modelformset_factory(PartnerLeadAgreement, form=PartnerLeadAgreementForm, extra=0, can_delete=False)
