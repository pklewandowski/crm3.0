# Generated by Django 5.0.7 on 2024-07-27 12:46

import django.contrib.auth.models
import django.contrib.postgres.fields
import django.db.models.deletion
import django.utils.timezone
import py3ws.utils.validators
import simple_history.models
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('address', '0001_initial'),
        ('attachment', '0001_initial'),
        ('auth', '0013_group_description'),
        ('hierarchy', '0001_initial'),
        ('note', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserBatchUploadBuffer',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('process_id', models.UUIDField()),
                ('first_name', models.CharField(blank=True, max_length=300, null=True)),
                ('last_name', models.CharField(blank=True, max_length=300, null=True)),
                ('company_name', models.CharField(blank=True, max_length=300, null=True)),
                ('tags', models.CharField(blank=True, max_length=300, null=True)),
                ('phone_one', models.CharField(blank=True, max_length=300, null=True)),
                ('email', models.CharField(blank=True, max_length=300, null=True)),
                ('adviser_email', models.CharField(blank=True, max_length=300, null=True)),
                ('broker_email', models.CharField(blank=True, max_length=300, null=True)),
                ('adviser', models.IntegerField(blank=True, null=True)),
                ('broker', models.IntegerField(blank=True, null=True)),
                ('personal_id', models.CharField(blank=True, max_length=30, null=True)),
                ('nip', models.CharField(blank=True, max_length=30, null=True)),
                ('regon', models.CharField(blank=True, max_length=30, null=True)),
                ('krs', models.CharField(blank=True, max_length=30, null=True)),
                ('city', models.CharField(blank=True, max_length=200, null=True)),
                ('street', models.CharField(blank=True, max_length=200, null=True)),
                ('street_no', models.CharField(blank=True, max_length=50, null=True)),
                ('apartment_no', models.CharField(blank=True, max_length=50, null=True)),
                ('post_code', models.CharField(blank=True, max_length=300, null=True)),
                ('errors', models.JSONField(default=list)),
                ('sq', models.IntegerField()),
            ],
            options={
                'db_table': 'user_batch_upload_buffer',
            },
        ),
        migrations.CreateModel(
            name='UserBatchUploadLog',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('created_by', models.CharField(max_length=300)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('row_count', models.IntegerField(null=True)),
            ],
            options={
                'db_table': 'user_batch_upload_log',
            },
        ),
        migrations.CreateModel(
            name='UserGroups',
            fields=[
                ('group_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='auth.group')),
            ],
            bases=('auth.group',),
            managers=[
                ('objects', django.contrib.auth.models.GroupManager()),
            ],
        ),
        migrations.CreateModel(
            name='UserRelationType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('left_name', models.CharField(max_length=300)),
                ('right_name', models.CharField(max_length=300)),
                ('is_direction', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'user_relation_type',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('avatar_filename', models.CharField(blank=True, max_length=300, null=True, verbose_name='user.avatar_filename')),
                ('avatar_base64', models.TextField(blank=True, null=True, verbose_name='user.avatar_base64')),
                ('username', models.CharField(max_length=150, unique=True, verbose_name='user.username')),
                ('first_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='user.first_name')),
                ('second_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='user.second_name')),
                ('third_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='user.third_name')),
                ('last_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='user.last_name')),
                ('is_company', models.BooleanField(blank=True, default=False, null=True, verbose_name='user.is_company')),
                ('company_name', models.CharField(blank=True, max_length=200, null=True, verbose_name='user.company_name')),
                ('company_legal_form', models.CharField(blank=True, max_length=200, null=True, verbose_name='user.company_legal_form')),
                ('company_establish_date', models.DateField(blank=True, null=True, verbose_name='user.company_establish_date')),
                ('company_activity_description', models.TextField(blank=True, null=True, verbose_name='user.company_activity_description')),
                ('company_activity_status', models.CharField(blank=True, choices=[('ACT', 'aktywna'), ('INACT', 'nieaktywna')], max_length=50, null=True, verbose_name='user.company_activity_status')),
                ('company_shareholder_count', models.IntegerField(blank=True, null=True, verbose_name='user.company_shareholder_count')),
                ('contractor_type', models.CharField(blank=True, max_length=50, null=True, verbose_name='user.contractor_type')),
                ('www_site', models.URLField(blank=True, null=True, verbose_name='user.www_site')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True, verbose_name='user.email')),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('personal_id', models.CharField(blank=True, max_length=20, null=True, unique=True, validators=[py3ws.utils.validators.pesel_validator], verbose_name='user.personal_id')),
                ('identity_card_no', models.CharField(blank=True, max_length=20, null=True, unique=True, verbose_name='user.identity_card_no')),
                ('identity_card_release_date', models.DateField(blank=True, null=True, verbose_name='user.identity_card_release_date')),
                ('identity_card_expiration_date', models.DateField(blank=True, null=True, verbose_name='user.identity_card_expiration_date')),
                ('passport_no', models.CharField(blank=True, max_length=20, null=True, unique=True, verbose_name='user.passport_no')),
                ('nip', models.CharField(blank=True, max_length=20, null=True, unique=True, validators=[py3ws.utils.validators.nip_validator], verbose_name='user.nip')),
                ('krs', models.CharField(blank=True, max_length=20, null=True, unique=True, validators=[py3ws.utils.validators.krs_validator], verbose_name='user.krs')),
                ('regon', models.CharField(blank=True, max_length=20, null=True, unique=True, validators=[py3ws.utils.validators.regon_validator], verbose_name='user.regon')),
                ('phone_one', models.CharField(blank=True, max_length=20, null=True, verbose_name='user.phone_one')),
                ('phone_two', models.CharField(blank=True, max_length=20, null=True, verbose_name='user.phone_two')),
                ('initial_password', models.CharField(blank=True, max_length=50, null=True, verbose_name='user.initial_password')),
                ('password_valid', models.BooleanField(default=False, verbose_name='user.password_valid')),
                ('ldap', models.BooleanField(default=False, verbose_name='user.ldap')),
                ('marital_status', models.CharField(blank=True, max_length=10, null=True, verbose_name='user.martial_status')),
                ('community_of_property', models.BooleanField(blank=True, null=True, verbose_name='user.community_of_property')),
                ('status', models.CharField(default='ACT', max_length=50, verbose_name='user.status')),
                ('description', models.TextField(blank=True, null=True, verbose_name='user.description')),
                ('sex', models.CharField(default='X', max_length=1, null=True)),
                ('representative', models.CharField(blank=True, choices=[('', ''), ('PZ', 'Prezes Zarządu'), ('CZ', 'Członek Zarządu'), ('WL', 'Właściciel'), ('WSO', 'Wspólnik Spółki Osobowej'), ('PL', 'Pełnomocnik')], max_length=10, null=True, verbose_name='user.representative')),
                ('tags', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, null=True, size=None)),
                ('process_id', models.UUIDField(blank=True, null=True)),
                ('company_address', models.ForeignKey(blank=True, db_column='id_company_address', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='company_address', to='address.address')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('home_address', models.ForeignKey(blank=True, db_column='id_home_address', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='home_address', to='address.address')),
                ('mail_address', models.ForeignKey(blank=True, db_column='id_mail_address', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mail_address', to='address.address')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Użytkownik',
                'verbose_name_plural': 'Użytkownicy',
                'db_table': 'user',
                'permissions': (('list_user', 'permissions.app.user.list_user'), ('view_user', 'permissions.app.user.view_user'), ('activate_user', 'permissions.app.user.activate_user'), ('changepassword_user', 'permissions.app.user.changepassword_user'), ('resetpassword_user', 'permissions.app.user.resetpassword_user'), ('viewinitialpassword_user', 'permissions.app.user.viewinitialpassword_user'), ('add_groupuser', 'permissions.app.user.add_groupuser'), ('change_groupuser', 'permissions.app.user.change_groupuser'), ('activate_groupuser', 'permissions.app.user.activate_groupuser'), ('list_groupuser', 'permissions.app.user.list_groupuser'), ('anonimize', 'permissions.app.user.anonimize')),
                'default_permissions': ('add', 'change'),
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalUser',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('avatar_filename', models.CharField(blank=True, max_length=300, null=True, verbose_name='user.avatar_filename')),
                ('avatar_base64', models.TextField(blank=True, null=True, verbose_name='user.avatar_base64')),
                ('username', models.CharField(db_index=True, max_length=150, verbose_name='user.username')),
                ('first_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='user.first_name')),
                ('second_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='user.second_name')),
                ('third_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='user.third_name')),
                ('last_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='user.last_name')),
                ('is_company', models.BooleanField(blank=True, default=False, null=True, verbose_name='user.is_company')),
                ('company_name', models.CharField(blank=True, max_length=200, null=True, verbose_name='user.company_name')),
                ('company_legal_form', models.CharField(blank=True, max_length=200, null=True, verbose_name='user.company_legal_form')),
                ('company_establish_date', models.DateField(blank=True, null=True, verbose_name='user.company_establish_date')),
                ('company_activity_description', models.TextField(blank=True, null=True, verbose_name='user.company_activity_description')),
                ('company_activity_status', models.CharField(blank=True, choices=[('ACT', 'aktywna'), ('INACT', 'nieaktywna')], max_length=50, null=True, verbose_name='user.company_activity_status')),
                ('company_shareholder_count', models.IntegerField(blank=True, null=True, verbose_name='user.company_shareholder_count')),
                ('contractor_type', models.CharField(blank=True, max_length=50, null=True, verbose_name='user.contractor_type')),
                ('www_site', models.URLField(blank=True, null=True, verbose_name='user.www_site')),
                ('email', models.EmailField(blank=True, db_index=True, max_length=254, null=True, verbose_name='user.email')),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('personal_id', models.CharField(blank=True, db_index=True, max_length=20, null=True, validators=[py3ws.utils.validators.pesel_validator], verbose_name='user.personal_id')),
                ('identity_card_no', models.CharField(blank=True, db_index=True, max_length=20, null=True, verbose_name='user.identity_card_no')),
                ('identity_card_release_date', models.DateField(blank=True, null=True, verbose_name='user.identity_card_release_date')),
                ('identity_card_expiration_date', models.DateField(blank=True, null=True, verbose_name='user.identity_card_expiration_date')),
                ('passport_no', models.CharField(blank=True, db_index=True, max_length=20, null=True, verbose_name='user.passport_no')),
                ('nip', models.CharField(blank=True, db_index=True, max_length=20, null=True, validators=[py3ws.utils.validators.nip_validator], verbose_name='user.nip')),
                ('krs', models.CharField(blank=True, db_index=True, max_length=20, null=True, validators=[py3ws.utils.validators.krs_validator], verbose_name='user.krs')),
                ('regon', models.CharField(blank=True, db_index=True, max_length=20, null=True, validators=[py3ws.utils.validators.regon_validator], verbose_name='user.regon')),
                ('phone_one', models.CharField(blank=True, max_length=20, null=True, verbose_name='user.phone_one')),
                ('phone_two', models.CharField(blank=True, max_length=20, null=True, verbose_name='user.phone_two')),
                ('initial_password', models.CharField(blank=True, max_length=50, null=True, verbose_name='user.initial_password')),
                ('password_valid', models.BooleanField(default=False, verbose_name='user.password_valid')),
                ('ldap', models.BooleanField(default=False, verbose_name='user.ldap')),
                ('marital_status', models.CharField(blank=True, max_length=10, null=True, verbose_name='user.martial_status')),
                ('community_of_property', models.BooleanField(blank=True, null=True, verbose_name='user.community_of_property')),
                ('status', models.CharField(default='ACT', max_length=50, verbose_name='user.status')),
                ('description', models.TextField(blank=True, null=True, verbose_name='user.description')),
                ('sex', models.CharField(default='X', max_length=1, null=True)),
                ('representative', models.CharField(blank=True, choices=[('', ''), ('PZ', 'Prezes Zarządu'), ('CZ', 'Członek Zarządu'), ('WL', 'Właściciel'), ('WSO', 'Wspólnik Spółki Osobowej'), ('PL', 'Pełnomocnik')], max_length=10, null=True, verbose_name='user.representative')),
                ('tags', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, null=True, size=None)),
                ('process_id', models.UUIDField(blank=True, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('company_address', models.ForeignKey(blank=True, db_column='id_company_address', db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='address.address')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('home_address', models.ForeignKey(blank=True, db_column='id_home_address', db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='address.address')),
                ('mail_address', models.ForeignKey(blank=True, db_column='id_mail_address', db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='address.address')),
            ],
            options={
                'verbose_name': 'historical Użytkownik',
                'verbose_name_plural': 'historical Użytkownicy',
                'db_table': 'h_user',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalUserGroups',
            fields=[
                ('group_ptr', models.ForeignKey(auto_created=True, blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, parent_link=True, related_name='+', to='auth.group')),
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=150, verbose_name='name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='group.description')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical user groups',
                'verbose_name_plural': 'historical user groupss',
                'db_table': 'h_user_groups',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='UserAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, null=True)),
                ('is_dir', models.BooleanField(default=False)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('attachment', models.ForeignKey(db_column='id_attachment', null=True, on_delete=django.db.models.deletion.CASCADE, to='attachment.attachment')),
                ('created_by', models.ForeignKey(db_column='id_created_by', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('document', models.ForeignKey(db_column='id_document', on_delete=django.db.models.deletion.CASCADE, related_name='attachment_set', to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(db_column='id_parent', null=True, on_delete=django.db.models.deletion.CASCADE, to='user.userattachment')),
            ],
            options={
                'db_table': 'user_attachment',
            },
        ),
        migrations.CreateModel(
            name='UserHierarchy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hierarchy', models.ForeignKey(db_column='id_hierarchy', on_delete=django.db.models.deletion.CASCADE, related_name='hierarchy', to='hierarchy.hierarchy')),
                ('user', models.ForeignKey(db_column='id_user', on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_hierarchy',
            },
        ),
        migrations.AddField(
            model_name='user',
            name='hierarchy',
            field=models.ManyToManyField(through='user.UserHierarchy', to='hierarchy.hierarchy'),
        ),
        migrations.CreateModel(
            name='UserHierarchyPosition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.ForeignKey(db_column='id_position', on_delete=django.db.models.deletion.CASCADE, to='hierarchy.hierarchyposition')),
                ('user', models.ForeignKey(db_column='id_user', on_delete=django.db.models.deletion.CASCADE, related_name='position_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_hierarchy_position',
            },
        ),
        migrations.AddField(
            model_name='user',
            name='position',
            field=models.ManyToManyField(through='user.UserHierarchyPosition', to='hierarchy.hierarchyposition'),
        ),
        migrations.CreateModel(
            name='UserNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.ForeignKey(db_column='id_note', on_delete=django.db.models.deletion.CASCADE, to='note.note')),
                ('user', models.ForeignKey(db_column='id_user', on_delete=django.db.models.deletion.CASCADE, related_name='note_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_note',
                'ordering': ['user', '-note__creation_date'],
            },
        ),
        migrations.AddField(
            model_name='user',
            name='notes',
            field=models.ManyToManyField(through='user.UserNote', to='note.note'),
        ),
        migrations.CreateModel(
            name='HistoricalUserRelation',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('description', models.TextField(blank=True, null=True, verbose_name='user.relation.description')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('left', models.ForeignKey(blank=True, db_column='id_user_left', db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='user.relation.left')),
                ('right', models.ForeignKey(blank=True, db_column='id_user_right', db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='user.relation.right')),
                ('type', models.ForeignKey(blank=True, db_column='id_type', db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='user.userrelationtype', verbose_name='user.relation.type')),
            ],
            options={
                'verbose_name': 'historical user relation',
                'verbose_name_plural': 'historical user relations',
                'db_table': 'h_user_relation',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='UserRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, null=True, verbose_name='user.relation.description')),
                ('left', models.ForeignKey(db_column='id_user_left', on_delete=django.db.models.deletion.CASCADE, related_name='user_left_set', to=settings.AUTH_USER_MODEL, verbose_name='user.relation.left')),
                ('right', models.ForeignKey(db_column='id_user_right', on_delete=django.db.models.deletion.CASCADE, related_name='user_right_set', to=settings.AUTH_USER_MODEL, verbose_name='user.relation.right')),
                ('type', models.ForeignKey(db_column='id_type', on_delete=django.db.models.deletion.CASCADE, to='user.userrelationtype', verbose_name='user.relation.type')),
            ],
            options={
                'db_table': 'user_relation',
                'unique_together': {('left', 'right', 'type')},
            },
        ),
    ]