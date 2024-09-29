from django.db.models import JSONField
from django.db import models

import py3ws.model.mixin


class Config(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50)
    value = JSONField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'config'


class HoldingCompany(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    is_default = models.BooleanField(default=False)
    email_server_name = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'holding_company'


class FormAttribute(models.Model):
    form_name = models.CharField(max_length=300, verbose_name='form.attribute.form_name')
    attributes = JSONField(null=True, blank=True, default=dict, verbose_name='form.attribute.attributes')

    def __str__(self):
        return self.form_name

    class Meta:
        db_table = 'form_attribute'
