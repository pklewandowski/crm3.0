# Generated by Django 5.0.7 on 2024-07-27 12:46

import django.core.validators
import simple_history.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalMessageTemplate',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('subject', models.CharField(blank=True, max_length=500, null=True, verbose_name='message.template.subject')),
                ('name', models.CharField(max_length=200, verbose_name='message.template.name')),
                ('code', models.CharField(max_length=20, validators=[django.core.validators.RegexValidator(message='Kod niezgodny z wzorcem', regex='^[A-Z][A-Z_]*[A-Z]$')], verbose_name='message.template.code')),
                ('text', models.TextField(blank=True, null=True, verbose_name='message.template.text')),
                ('sms_text', models.TextField(blank=True, null=True, verbose_name='message.template.sms_text')),
                ('creation_date', models.DateTimeField(blank=True, editable=False)),
                ('type', models.CharField(default='TMPL', max_length=10, verbose_name='message.template.type')),
                ('editable', models.BooleanField(default=True, verbose_name='message.template.editable')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical message template',
                'verbose_name_plural': 'historical message templates',
                'db_table': 'h_message_template',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='MessageQueue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=500)),
                ('recipients', models.JSONField(null=True)),
                ('phones', models.JSONField(null=True)),
                ('text', models.TextField(blank=True, null=True)),
                ('sms_text', models.TextField(blank=True, null=True)),
                ('status', models.CharField(default='NW', max_length=3)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('is_sent', models.BooleanField(default=False)),
                ('send_date', models.DateTimeField(null=True)),
                ('attachments', models.JSONField(null=True)),
            ],
            options={
                'db_table': 'message_queue',
            },
        ),
        migrations.CreateModel(
            name='MessageTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(blank=True, max_length=500, null=True, verbose_name='message.template.subject')),
                ('name', models.CharField(max_length=200, verbose_name='message.template.name')),
                ('code', models.CharField(max_length=20, validators=[django.core.validators.RegexValidator(message='Kod niezgodny z wzorcem', regex='^[A-Z][A-Z_]*[A-Z]$')], verbose_name='message.template.code')),
                ('text', models.TextField(blank=True, null=True, verbose_name='message.template.text')),
                ('sms_text', models.TextField(blank=True, null=True, verbose_name='message.template.sms_text')),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(default='TMPL', max_length=10, verbose_name='message.template.type')),
                ('editable', models.BooleanField(default=True, verbose_name='message.template.editable')),
            ],
            options={
                'db_table': 'message_template',
            },
        ),
        migrations.CreateModel(
            name='MessageTemplateParam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=200, verbose_name='message.template.param.name')),
                ('type', models.CharField(max_length=10, verbose_name='message.template.param.name')),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'message_template_param',
            },
        ),
        migrations.CreateModel(
            name='MessageTemplateParamDefinition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='message.template.param.definition.name')),
                ('code', models.CharField(max_length=200, unique=True, verbose_name='message.template.param.definition.code')),
                ('type', models.CharField(default='model', max_length=50, verbose_name='message.template.param.definition.type')),
                ('model', models.CharField(blank=True, max_length=200, null=True, verbose_name='message.template.param.definition.model')),
                ('field', models.CharField(blank=True, max_length=200, null=True, verbose_name='message.template.param.definition.field')),
                ('test_value', models.CharField(default='xxx', max_length=200, verbose_name='message.template.param.definition.test_value')),
                ('description', models.TextField(blank=True, null=True, verbose_name='message.template.param.definition.description')),
            ],
            options={
                'db_table': 'message_template_param_definition',
            },
        ),
    ]
