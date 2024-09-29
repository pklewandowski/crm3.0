from django import forms
from django.forms import formset_factory

from django.utils.translation import gettext_lazy as _

from apps.product.utils.utils import ProductUtils
from py3ws.forms import p3form

from apps.message.models import MessageTemplate


class DocumentTypeRuleForm(p3form.Form):
    AFTER_BEFORE = [('', ''), ('BEFORE', 'przed'), ('AFTER', 'po')]
    CONDITIONAL_OPERATOR = [('', ''), ('=', '='), ('!=', '!='), ('<', '<'), ('<=', '<='), ('>', '>'), ('>=', '>='), ('IN', 'w'), ('NOT_IN', 'nie')]
    CONDITION = [
        ('', ''),
        ('INSTALMENT_OVERDUE_OCCURRENCE', _('liczba wystąpień zaległości')),
        ('INSTALMENT_OVERDUE_COUNT', _('liczba kolejnych zaległych rat')),
        # ('DOCUMENT_STATUS', _('status pożyczki')),
    ]
    WHAT = [
        ('', ''),
        ('raty',
         tuple([
             ('EACH_INSTALMENT', _('każda rata')),
             # ('EACH_OVERDUE_INSTALMENT', _('każda zaległa rata')),
         ]
         )),
        ('umowa',
         tuple([
             ('AGR_CANCEL', _('wypowiedzenie umowy')),
             ('AGR_END', _('zakończenie umowy')),
             ('AGR_CLOSE', _('rozliczenie umowy'))
         ]
         ))
    ]

    days = forms.IntegerField(widget=forms.TextInput, required=False)
    after_before = forms.ChoiceField(choices=AFTER_BEFORE, required=False)
    what = forms.ChoiceField(choices=WHAT, required=False)
    condition = forms.ChoiceField(choices=CONDITION, required=False)
    rule_conditional_value = forms.IntegerField(label=None, widget=forms.TextInput, required=False)
    rule_conditional_operator = forms.ChoiceField(choices=CONDITIONAL_OPERATOR, required=False)
    rule_status_change_from = forms.ChoiceField(required=False, label='Zmień status z')
    rule_status_change_to = forms.CharField(label='Zmień status na', widget=forms.Select, required=False)
    rule_send_sms = forms.CharField(label=_('Wyślij SMS do klienta'), widget=forms.Select, required=False)
    rule_send_email = forms.CharField(label=_('Wyślij e-mail do klienta'), widget=forms.Select, required=False)
    rule_send_sms_to_employees = forms.CharField(label=_('Wyślij SMS'), widget=forms.CheckboxInput, required=False)
    rule_send_email_to_employees = forms.CharField(label=_('Wyślij e-mail'), widget=forms.CheckboxInput, required=False)
    rule_send_letter = forms.CharField(label=_('Wyślij pismo'), widget=forms.Select, required=False)
    rule_generate_alert_for = forms.CharField(max_length=500, label=_('Wygeneruj powiadomienia do'), required=False)
    rule_generate_alert_text = forms.CharField(max_length=500, label=_('o treści'), widget=forms.Textarea, required=False)
    rule_run_method = forms.CharField(max_length=300, label=_('Uruchom metodę'), required=False)
    sq = forms.IntegerField(widget=forms.TextInput, required=False)

    def __init__(self, *args, **kwargs):
        document_type = kwargs.pop('document_type')
        super().__init__(*args, **kwargs)
        self.fields['rule_status_change_from'].choices = [('', '')] + [(i.pk, i.name) for i in document_type.product_status_set.all().order_by('sq')]
        self.fields['sq'].widget.attrs['readonly'] = True
        self.fields['rule_conditional_value'].widget.attrs['class'] += ' rule-conditional-value'
        self.fields['days'].widget.attrs['class'] += ' rule-days'
        self.fields['after_before'].widget.attrs['class'] += ' rule-after-before'
        self.fields['what'].widget.attrs['class'] += ' rule-what'
        self.fields['condition'].widget.attrs['class'] += ' rule-condition'
        self.fields['rule_conditional_operator'].widget.attrs['class'] += ' rule-conditional-operator'
        self.fields['rule_status_change_from'].widget.attrs['class'] += ' rule-status-change-from'
        self.fields['rule_status_change_to'].widget.attrs['class'] += ' rule-status-change-to'
        self.fields['rule_generate_alert_for'].widget.attrs['class'] += ' rule-generate-alert-for'
        self.fields['sq'].widget.attrs['class'] += ' rule-sq'

        self.fields['rule_send_sms'].widget.choices = [('', '')] + [(i.pk, i.name) for i in MessageTemplate.objects.filter(type='TMPL', sms_text__isnull=False)]
        self.fields['rule_send_email'].widget.choices = [('', '')] + [(i.pk, i.name) for i in MessageTemplate.objects.filter(type='TMPL', text__isnull=False)]

        if self.initial and 'rule_status_change_from' in self.initial and self.initial['rule_status_change_from']:
            self.fields['rule_status_change_to'].widget.choices = [(i.available_status.pk, i.available_status.name) for i in ProductUtils.get_available_statuses(self.initial['rule_status_change_from'])]


DocumentTypeActionFormset = formset_factory(DocumentTypeRuleForm, extra=0, can_delete=True)
