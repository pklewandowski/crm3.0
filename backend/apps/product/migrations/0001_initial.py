# Generated by Django 5.0.7 on 2024-07-27 12:46

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
import simple_history.models
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('hierarchy', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyBankTransactionFile',
            fields=[
                ('company', models.OneToOneField(db_column='id_company', on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='bank_transaction_file', serialize=False, to='hierarchy.hierarchy')),
                ('base_dir', models.CharField(default='', max_length=200)),
                ('subdir', models.CharField(default='', max_length=200)),
            ],
            options={
                'db_table': 'product_company_bank_transaction_file',
            },
        ),
        migrations.CreateModel(
            name='HistoricalProductInterest',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('start_date', models.DateField(verbose_name='product.interest.start_date')),
                ('delay_rate', models.DecimalField(decimal_places=4, max_digits=10, verbose_name='product.interest.delay_rate')),
                ('delay_max_rate', models.DecimalField(decimal_places=4, max_digits=10, verbose_name='product.interest.delay_max_rate')),
                ('statutory_rate', models.DecimalField(decimal_places=4, max_digits=10, verbose_name='product.interest.statutory_rate')),
                ('is_set_globally', models.BooleanField(default=False, verbose_name='product.interest.is_set_globally')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical product interest',
                'verbose_name_plural': 'historical product interests',
                'db_table': 'h_product_interest',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agreement_no', models.CharField(max_length=100, unique=True, verbose_name='product.agreement_no')),
                ('start_date', models.DateField(verbose_name='product.start_date')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='product.end_date')),
                ('termination_date', models.DateField(blank=True, null=True, verbose_name='product.termination_date')),
                ('capitalization_date', models.DateField(blank=True, null=True, verbose_name='product.capitalization_date')),
                ('creation_date', models.DateTimeField(verbose_name='product.creation_date')),
                ('recount_required_date', models.DateField(blank=True, null=True, verbose_name='product.recount_required_date')),
                ('recount_required_date_creation_marker', models.DateTimeField(blank=True, null=True)),
                ('creditor_bank_account', models.CharField(blank=True, max_length=28, null=True, verbose_name='product.creditor_bank_account')),
                ('debtor_bank_account', models.CharField(blank=True, max_length=28, null=True, verbose_name='product.debtor_bank_account')),
                ('value', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='product.value')),
                ('balance', models.DecimalField(decimal_places=2, default=Decimal('-1'), max_digits=10, verbose_name='product.value')),
                ('capital_net', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='product.capital_net')),
                ('commission', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='product.commision')),
                ('instalment_capital', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='product.instalment_capital')),
                ('instalment_commission', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='product.instalment_commission')),
                ('instalment_interest_rate', models.DecimalField(decimal_places=4, default=0, max_digits=10, verbose_name='product.instalment_interest')),
                ('grace_period', models.IntegerField(default=0, verbose_name='product.grace_period')),
                ('debt_collection_fee_period', models.IntegerField(default=0, verbose_name='product.debt_collection_fee_period')),
                ('debt_collection_fee', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='product.debt_collection_fee')),
                ('interest_for_delay_rate_use', models.CharField(default='XXX', max_length=10, verbose_name='product.interest_for_delay_rate_use')),
                ('interest_for_delay_calculation_add_value', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='product.interest_for_delay_calculation_add_value')),
                ('capital_type_calc_source', models.CharField(default='G', max_length=10, verbose_name='product.capital_type_calc_source')),
            ],
            options={
                'db_table': 'product',
                'permissions': (('add:all', 'product.permissions.add.all'), ('add:own', 'product.permissions.add.own'), ('change:all', 'product.permissions.change.all'), ('change:own', 'product.permissions.change.own'), ('list:all', 'product.permissions.list.all'), ('list:own', 'product.permissions.list.own'), ('view:all', 'product.permissions.view.all'), ('view:own', 'product.permissions.view.own')),
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='ProductAccounting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sq', models.IntegerField()),
            ],
            options={
                'db_table': 'product_accounting',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='ProductAction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300, verbose_name='product.action.name')),
                ('description', models.CharField(blank=True, max_length=500, null=True, verbose_name='product.action.description')),
                ('cost', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='product.action.cost')),
                ('send_date', models.DateField(blank=True, null=True, verbose_name='product.action.send_date')),
                ('receive_date', models.DateField(blank=True, null=True, verbose_name='product.action.receive_date')),
                ('action_date', models.DateTimeField(verbose_name='product.action.action_date')),
                ('action_execution_date', models.DateField(null=True, verbose_name='product.action.action_execution_date')),
                ('datasource', models.JSONField(null=True)),
            ],
            options={
                'db_table': 'product_action',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='ProductActionAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'product_action_attachment',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='ProductActionDefinition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300, verbose_name='product.action.definition.name')),
                ('sq', models.IntegerField()),
            ],
            options={
                'db_table': 'product_action_definition',
            },
        ),
        migrations.CreateModel(
            name='ProductAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'product_attachment',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='ProductCalculation',
            fields=[
                ('id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('calc_date', models.DateField(verbose_name='product.calculation.calc_date')),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.capital_per_day')),
                ('capital_per_day', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.capital_per_day')),
                ('capital_not_required', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.capital_not_required')),
                ('capital_required', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.capital_required')),
                ('capital_required_from_schedule', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='product.calculation.capital_required_from_schedule')),
                ('interest_daily', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.interest_daily')),
                ('interest_per_day', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.interest_per_day')),
                ('interest_cumulated_per_day', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.interest_cumulated_per_day')),
                ('interest_required', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.interest_required')),
                ('interest_required_from_schedule', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.interest_required_from_schedule')),
                ('interest_rate', models.DecimalField(decimal_places=2, default=0, max_digits=10, null=True, verbose_name='product.calculation.interest_rate')),
                ('interest_for_delay_calculation_base', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.interest_for_delay_calculation_base')),
                ('interest_for_delay_total', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.interest_for_delay_total')),
                ('interest_for_delay_rate', models.DecimalField(decimal_places=2, default=0, max_digits=10, null=True, verbose_name='product.calculation.interest_for_delay_rate')),
                ('interest_for_delay_required', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.interest_for_delay_required')),
                ('interest_for_delay_required_daily', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.interest_for_delay_required_daily')),
                ('commission_per_day', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.commission_per_day')),
                ('commission_required', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.commission_required')),
                ('commission_not_required', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.commission_total')),
                ('commission_required_from_schedule', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.commission_required_from_schedule')),
                ('required_liabilities_sum', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.required_liabilities_sum')),
                ('required_liabilities_sum_from_schedule', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.required_liabilities_sum_from_schedule')),
                ('cost_occurrence', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.cost_occurence')),
                ('cost', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.interest_required_daily')),
                ('cost_total', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.cost_total')),
                ('instalment', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.instalment')),
                ('instalment_total', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.instalment_total')),
                ('instalment_overpaid', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.instalment_overpaid')),
                ('instalment_accounting_capital_required', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.instalment_capital_required')),
                ('instalment_accounting_capital_not_required', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.instalment_capital_not_required')),
                ('instalment_accounting_commission_required', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.instalment_commission_required')),
                ('instalment_accounting_commission_not_required', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.instalment_commission_not_required')),
                ('instalment_accounting_interest_required', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.instalment_interest_required')),
                ('instalment_accounting_interest_for_delay', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.instalment_instalment_interest')),
                ('instalment_accounting_cost', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='product.calculation.instalment_cost')),
                ('instalment_overdue_count', models.IntegerField(default=0)),
                ('instalment_overdue_occurrence', models.IntegerField(default=0)),
                ('remission_capital', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.remission_capital')),
                ('remission_commission', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.remission_commission')),
                ('remission_interest', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.remission_interest')),
                ('remission_interest_for_delay', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.remission_interest_for_delay')),
                ('remission_cost', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='product.calculation.remission_cost')),
            ],
            options={
                'db_table': 'product_calculation',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='ProductCashFlow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_uid', models.CharField(blank=True, max_length=100, null=True)),
                ('subtype', models.CharField(blank=True, max_length=10, null=True)),
                ('value', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='product.cash.flow.value')),
                ('cash_flow_date', models.DateField(blank=True, null=True, verbose_name='product.cash.flow.cash_flow_date')),
                ('accounting_date', models.DateField(blank=True, null=True, verbose_name='product.cash.flow.accounting_date')),
                ('entry_source', models.CharField(default='HAND', max_length=10, verbose_name='product.cash.flow.entry_source')),
                ('description', models.CharField(blank=True, max_length=500, null=True)),
                ('editable', models.BooleanField(default=True)),
                ('calculable', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'product_cash_flow',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='ProductClient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'product_client',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='ProductCommission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='product.commission.value')),
                ('name', models.CharField(blank=True, max_length=200, null=True, verbose_name='product.commission.name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='product.commission.name')),
                ('is_active', models.BooleanField(default=True, verbose_name='product.commission.is_active')),
                ('date_from', models.DateField(blank=True, null=True, verbose_name='product.commission.date_from')),
                ('date_to', models.DateField(blank=True, null=True, verbose_name='product.commission.date_to')),
            ],
            options={
                'db_table': 'product_commission',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='ProductInterest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(verbose_name='product.interest.start_date')),
                ('delay_rate', models.DecimalField(decimal_places=4, max_digits=10, verbose_name='product.interest.delay_rate')),
                ('delay_max_rate', models.DecimalField(decimal_places=4, max_digits=10, verbose_name='product.interest.delay_max_rate')),
                ('statutory_rate', models.DecimalField(decimal_places=4, max_digits=10, verbose_name='product.interest.statutory_rate')),
                ('is_set_globally', models.BooleanField(default=False, verbose_name='product.interest.is_set_globally')),
            ],
            options={
                'db_table': 'product_interest',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='ProductInterestGlobal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(unique=True, verbose_name='product.interest.global.start_date')),
                ('interest_for_delay_rate', models.DecimalField(decimal_places=4, max_digits=10, verbose_name='product.interest.global.interest_for_delay_rate')),
                ('interest_max_for_delay_rate', models.DecimalField(decimal_places=4, max_digits=10, verbose_name='product.interest.global.interest_max_for_delay_rate')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='product.interest.global.creation_date')),
            ],
            options={
                'db_table': 'product_interest_global',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='ProductInterestType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='product.interest.type.name')),
                ('code', models.CharField(max_length=100, unique=True, verbose_name='product.interest.type.code')),
                ('description', models.TextField(blank=True, null=True, verbose_name='product.interest.type.description')),
                ('is_default', models.BooleanField(default=False, verbose_name='product.interest.type.is_default')),
                ('sq', models.IntegerField(db_column='sq')),
            ],
            options={
                'db_table': 'product_interest_type',
                'ordering': ['sq'],
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='ProductSchedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('maturity_date', models.DateField()),
                ('instalment_capital', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10)),
                ('instalment_interest', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10)),
                ('instalment_commission', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10)),
            ],
            options={
                'db_table': 'product_schedule',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='ProductStatusTrack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('effective_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('reason', models.TextField(null=True)),
                ('is_initial', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'product_status_track',
            },
        ),
        migrations.CreateModel(
            name='ProductTypeAction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sq', models.IntegerField()),
            ],
            options={
                'db_table': 'product_type_action',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='ProductTypeCommission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='product.type.commission.name')),
                ('type', models.CharField(max_length=3, verbose_name='product.type.commission.type')),
                ('period', models.CharField(max_length=3, verbose_name='product.type.commission.period')),
                ('calculation_type', models.CharField(max_length=20, verbose_name='product.type.commission.calculation_type')),
                ('default_value', models.DecimalField(decimal_places=2, max_digits=15, validators=[django.core.validators.MinValueValidator(0)], verbose_name='product.type.commission.default_value')),
            ],
            options={
                'db_table': 'product_type_commission',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='ProductTypeProcessFlow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_default', models.BooleanField(default=False)),
                ('sq', models.IntegerField()),
            ],
            options={
                'db_table': 'product_type_process_flow',
            },
        ),
        migrations.CreateModel(
            name='ProductTypeStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='product.type.status.name')),
                ('code', models.CharField(max_length=10, verbose_name='product.type.status.code')),
                ('is_initial', models.BooleanField(verbose_name='product.type.status.is_initial')),
                ('is_active', models.BooleanField(default=True, verbose_name='product.type.status.is_active')),
                ('is_alternate', models.BooleanField(default=False, verbose_name='product.type.status.is_alternate')),
                ('is_closing_process', models.BooleanField(default=False, verbose_name='product.type.status.is_closing_process')),
                ('action_class', models.CharField(blank=True, max_length=300, null=True)),
                ('action', models.CharField(blank=True, max_length=300, null=True)),
                ('color', models.CharField(default='ffffff', max_length=8, verbose_name='document.type.status.can_revert')),
                ('sq', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'product_type_status',
            },
        ),
    ]
