from django.db.models import JSONField
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords


class Message:
    class Meta:
        permissions = list()


class MessageTemplate(models.Model):
    subject = models.CharField(verbose_name=_('message.template.subject'), max_length=500, null=True, blank=True)
    name = models.CharField(verbose_name=_('message.template.name'), max_length=200)
    code = models.CharField(verbose_name=_('message.template.code'), max_length=20,
                            validators=[
                                RegexValidator(regex=r"^[A-Z][A-Z_]*[A-Z]$",
                                               message='Kod niezgodny z wzorcem',
                                               )
                            ])
    text = models.TextField(verbose_name=_('message.template.text'), null=True, blank=True)
    sms_text = models.TextField(verbose_name=_('message.template.sms_text'), null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    # typ szablonu - czy TMPL - wiadomość właściwa, czy INC - include (partial)
    type = models.CharField(verbose_name=_('message.template.type'), max_length=10, default='TMPL')
    editable = models.BooleanField(verbose_name=_('message.template.editable'), default=True)
    history = HistoricalRecords(table_name='h_message_template')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'message_template'


class MessageTemplateParam(models.Model):
    template = models.ForeignKey(MessageTemplate, db_column='id_template', related_name='params', on_delete=models.CASCADE)
    code = models.CharField(verbose_name=_('message.template.param.name'), max_length=200)
    type = models.CharField(verbose_name=_('message.template.param.name'), max_length=10)
    creation_date = models.DateTimeField(auto_now_add=True)

    # history = HistoricalRecords(table_name='h_message_template_param')

    class Meta:
        db_table = 'message_template_param'


class MessageTemplateParamDefinition(models.Model):
    name = models.CharField(verbose_name=_('message.template.param.definition.name'), max_length=200)
    code = models.CharField(verbose_name=_('message.template.param.definition.code'), max_length=200, unique=True)
    type = models.CharField(verbose_name=_('message.template.param.definition.type'), max_length=50, default='model')
    model = models.CharField(verbose_name=_('message.template.param.definition.model'), max_length=200, null=True, blank=True)
    field = models.CharField(verbose_name=_('message.template.param.definition.field'), max_length=200, null=True, blank=True)
    test_value = models.CharField(verbose_name=_('message.template.param.definition.test_value'), max_length=200, default='xxx')
    description = models.TextField(verbose_name=_('message.template.param.definition.description'), null=True, blank=True)

    class Meta:
        db_table = 'message_template_param_definition'


class MessageQueue(models.Model):
    subject = models.CharField(max_length=500)
    recipients = JSONField(null=True)
    phones = JSONField(null=True)
    template = models.ForeignKey(MessageTemplate, db_column='id_template', on_delete=models.CASCADE)
    text = models.TextField(null=True, blank=True)
    sms_text = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=3, default='NW')
    creation_date = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)
    send_date = models.DateTimeField(null=True)
    attachments = JSONField(null=True)

    class Meta:
        db_table = 'message_queue'
