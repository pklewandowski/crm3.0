# Generated by Django 5.1.3 on 2024-12-29 13:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0004_alter_documentstatuscourse_document'),
    ]

    operations = [
        migrations.AddField(
            model_name='documenttypeaccountingtype',
            name='parent',
            field=models.ForeignKey(blank=True, db_column='id_parent', null=True, on_delete=django.db.models.deletion.CASCADE, to='document.documenttypeaccountingtype'),
        ),
    ]
