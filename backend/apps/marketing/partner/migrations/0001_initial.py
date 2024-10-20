# Generated by Django 5.0.7 on 2024-07-27 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PartnerLead',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=200, null=True, verbose_name='parnter.lead.first_name')),
                ('last_name', models.CharField(max_length=200, null=True, verbose_name='parnter.lead.last_name')),
                ('company_name', models.CharField(max_length=300, null=True, verbose_name='parnter.lead.company_name')),
                ('nip', models.CharField(max_length=20, null=True, verbose_name='parnter.lead.nip')),
                ('phone', models.CharField(max_length=20, null=True, verbose_name='parnter.lead.phone')),
                ('email', models.EmailField(db_index=True, max_length=254, null=True, verbose_name='parnter.lead.email')),
                ('amount', models.IntegerField(null=True, verbose_name='parnter.lead.amount')),
                ('period', models.IntegerField(blank=True, null=True, verbose_name='parnter.lead.period')),
                ('security_location', models.CharField(max_length=200, null=True, verbose_name='parnter.lead.security_location_city')),
                ('partner_first_name', models.CharField(max_length=200, null=True, verbose_name='parnter.lead.partner_first_name')),
                ('partner_last_name', models.CharField(max_length=200, null=True, verbose_name='parnter.lead.partner_last_name')),
                ('partner_phone', models.CharField(max_length=20, null=True, verbose_name='parnter.lead.partner_phone')),
                ('partner_email', models.EmailField(max_length=254, null=True, verbose_name='parnter.lead.partner_email')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='parnter.lead.creation_date')),
                ('status', models.CharField(blank=True, default='NW', max_length=10, verbose_name='parnter.lead.creation_date')),
                ('prefered_adviser_email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='parnter.lead.prefered_adviser_email')),
                ('mortgage_register_no', models.CharField(blank=True, max_length=50, null=True, verbose_name='parnter.lead.mortgage_register_no')),
            ],
            options={
                'db_table': 'partner_lead',
                'permissions': (('view:all', 'permissions.app.partner.lead.view.all'), ('view:department', 'permissions.app.partner.lead.view.department'), ('view:position', 'permissions.app.partner.lead.view.position'), ('view:own', 'permissions.app.partner.lead.view.own'), ('list:all', 'permissions.app.partner.lead.list.all'), ('list:department', 'permissions.app.partner.lead.list.department'), ('list:position', 'permissions.app.partner.lead.list.position'), ('list:own', 'permissions.app.partner.lead.list.own'), ('add:all', 'permissions.app.partner.lead.add.all'), ('add:department', 'permissions.app.partner.lead.add.department'), ('add:position', 'permissions.app.partner.lead.add.position'), ('add:own', 'permissions.app.partner.lead.add.own'), ('change:all', 'permissions.app.partner.lead.change.all'), ('change:department', 'permissions.app.partner.lead.change.department'), ('change:position', 'permissions.app.partner.lead.change.position'), ('change:own', 'permissions.app.partner.lead.change.own')),
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='PartnerLeadAgreement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_checked', models.BooleanField(default=False)),
                ('check_date', models.DateTimeField(null=True)),
            ],
            options={
                'db_table': 'partner_lead_agreement',
                'ordering': ('agreement__sq',),
            },
        ),
        migrations.CreateModel(
            name='PartnerSecurityType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, null=True)),
                ('sq', models.IntegerField()),
            ],
            options={
                'db_table': 'partner_security_type',
            },
        ),
        migrations.CreateModel(
            name='PartnerAgreement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50)),
                ('version', models.CharField(max_length=20)),
                ('text', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('is_required', models.BooleanField(default=False)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.CharField(max_length=100)),
                ('sq', models.IntegerField()),
            ],
            options={
                'db_table': 'partner_agreement',
                'unique_together': {('code', 'version')},
            },
        ),
    ]
