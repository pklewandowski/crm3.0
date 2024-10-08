# Generated by Django 5.0.7 on 2024-07-27 12:46

import simple_history.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FileRepository',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='report.template.repo.name')),
                ('filename', models.CharField(blank=True, max_length=500, unique=True, verbose_name='report.template.repo.filename')),
                ('original_filename', models.CharField(blank=True, max_length=500, verbose_name='report.template.repo.original_filename')),
                ('mimetype', models.CharField(blank=True, max_length=100, verbose_name='report.template.repo.mimetype')),
                ('description', models.TextField(blank=True, null=True, verbose_name='report.template.repo.description')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='report.template.repo.creation_date')),
                ('created_by', models.CharField(blank=True, max_length=200, verbose_name='report.template.repo.created_by')),
                ('version', models.IntegerField(default=1, verbose_name='report.template.repo.created_by')),
            ],
            options={
                'db_table': 'file_repository',
            },
        ),
        migrations.CreateModel(
            name='HistoricalFileRepository',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='report.template.repo.name')),
                ('filename', models.CharField(blank=True, db_index=True, max_length=500, verbose_name='report.template.repo.filename')),
                ('original_filename', models.CharField(blank=True, max_length=500, verbose_name='report.template.repo.original_filename')),
                ('mimetype', models.CharField(blank=True, max_length=100, verbose_name='report.template.repo.mimetype')),
                ('description', models.TextField(blank=True, null=True, verbose_name='report.template.repo.description')),
                ('creation_date', models.DateTimeField(blank=True, editable=False, verbose_name='report.template.repo.creation_date')),
                ('created_by', models.CharField(blank=True, max_length=200, verbose_name='report.template.repo.created_by')),
                ('version', models.IntegerField(default=1, verbose_name='report.template.repo.created_by')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical file repository',
                'verbose_name_plural': 'historical file repositorys',
                'db_table': 'h_file_repository',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
