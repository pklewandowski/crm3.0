# Generated by Django 5.0.7 on 2024-07-27 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='StatGroupAdviser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='stat.group.adviser.name')),
                ('advisers', models.JSONField(blank=True, null=True, verbose_name='stat.group.adviser.advisers')),
            ],
            options={
                'db_table': 'stat_group_adviser',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='StatGroupLoanStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='stat.group.loan.name')),
                ('statuses', models.JSONField(blank=True, null=True, verbose_name='stat.group.loan.statuses')),
            ],
            options={
                'db_table': 'stat_group_loan_status',
                'ordering': ['name'],
            },
        ),
    ]