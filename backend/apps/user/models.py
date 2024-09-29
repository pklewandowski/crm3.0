import uuid

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group
from django.contrib.postgres.fields import ArrayField
from django.db.models import JSONField
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from apps.address.models import Address
from apps.attachment.models import Attachment
from apps.hierarchy.models import Hierarchy, HierarchyPosition
from apps.note.models import Note
from py3ws.utils.validators import pesel_validator, nip_validator, krs_validator, regon_validator

Group.add_to_class('description', models.TextField(verbose_name=_('group.description'), null=True, blank=True))


class User(AbstractUser):
    REPRESENTATIVE = [
        ('', ''),
        ('PZ', _('Prezes Zarządu')),
        ('CZ', _('Członek Zarządu')),
        ('WL', _('Właściciel')),
        ('WSO', _('Wspólnik Spółki Osobowej')),
        ('PL', _('Pełnomocnik')),
    ]
    home_address = models.ForeignKey(Address, null=True, blank=True, db_column='id_home_address', related_name='home_address', on_delete=models.CASCADE)
    company_address = models.ForeignKey(Address, null=True, blank=True, db_column='id_company_address', related_name='company_address', on_delete=models.CASCADE)
    mail_address = models.ForeignKey(Address, null=True, blank=True, db_column='id_mail_address', related_name='mail_address', on_delete=models.CASCADE)
    avatar_filename = models.CharField(verbose_name=_('user.avatar_filename'), max_length=300, null=True, blank=True)
    avatar_base64 = models.TextField(verbose_name=_('user.avatar_base64'), null=True, blank=True)
    username = models.CharField(verbose_name=_('user.username'), max_length=150, unique=True)
    first_name = models.CharField(verbose_name=_('user.first_name'), max_length=100, null=True, blank=True)
    second_name = models.CharField(verbose_name=_('user.second_name'), max_length=100, null=True, blank=True)
    third_name = models.CharField(verbose_name=_('user.third_name'), max_length=100, null=True, blank=True)
    last_name = models.CharField(verbose_name=_('user.last_name'), max_length=100, null=True, blank=True)

    is_company = models.BooleanField(verbose_name=_('user.is_company'), null=True, blank=True, default=False)
    company_name = models.CharField(verbose_name=_('user.company_name'), max_length=200, null=True, blank=True)
    company_legal_form = models.CharField(verbose_name=_('user.company_legal_form'), max_length=200, null=True, blank=True)
    company_establish_date = models.DateField(verbose_name=_('user.company_establish_date'), null=True, blank=True)
    company_activity_description = models.TextField(verbose_name=_('user.company_activity_description'), null=True, blank=True)
    company_activity_status = models.CharField(verbose_name=_('user.company_activity_status'), max_length=50, null=True, blank=True,
                                               choices=[('ACT', 'aktywna'), ('INACT', 'nieaktywna')])
    # Liczba udziałowców
    company_shareholder_count = models.IntegerField(verbose_name=_('user.company_shareholder_count'), null=True, blank=True)
    #  contractor type determines the business type of user ie. LAW_OFFICE
    contractor_type = models.CharField(verbose_name=_('user.contractor_type'), max_length=50, null=True, blank=True)
    www_site = models.URLField(verbose_name=_('user.www_site'), null=True, blank=True, )
    email = models.EmailField(verbose_name=_('user.email'), null=True, blank=True, unique=True)
    birth_date = models.DateField(null=True, blank=True)
    personal_id = models.CharField(verbose_name=_('user.personal_id'), max_length=20, null=True, blank=True, unique=True, validators=[pesel_validator])
    identity_card_no = models.CharField(verbose_name=_('user.identity_card_no'), max_length=20, null=True, blank=True, unique=True)
    identity_card_release_date = models.DateField(verbose_name=_('user.identity_card_release_date'), null=True, blank=True)
    identity_card_expiration_date = models.DateField(verbose_name=_('user.identity_card_expiration_date'), null=True, blank=True)
    passport_no = models.CharField(verbose_name=_('user.passport_no'), max_length=20, null=True, blank=True, unique=True)
    nip = models.CharField(verbose_name=_('user.nip'), max_length=20, null=True, blank=True, unique=True, validators=[nip_validator])
    krs = models.CharField(verbose_name=_('user.krs'), max_length=20, null=True, blank=True, unique=True, validators=[krs_validator])
    regon = models.CharField(verbose_name=_('user.regon'), max_length=20, null=True, blank=True, unique=True, validators=[regon_validator])
    phone_one = models.CharField(verbose_name=_('user.phone_one'), max_length=20, null=True, blank=True)
    phone_two = models.CharField(verbose_name=_('user.phone_two'), max_length=20, null=True, blank=True)
    initial_password = models.CharField(verbose_name=_('user.initial_password'), max_length=50, null=True, blank=True)
    password_valid = models.BooleanField(verbose_name=_('user.password_valid'), default=False)
    ldap = models.BooleanField(verbose_name=_('user.ldap'), default=False)
    marital_status = models.CharField(verbose_name=_('user.martial_status'), max_length=10, null=True, blank=True)
    #wspólnota majątkowa
    community_of_property = models.BooleanField(verbose_name=_('user.community_of_property'), null=True, blank=True)
    status = models.CharField(verbose_name=_('user.status'), max_length=50, default='ACT')
    description = models.TextField(verbose_name=_('user.description'), null=True, blank=True)
    sex = models.CharField(max_length=1, null=True, default='X')
    hierarchy = models.ManyToManyField(Hierarchy, through='UserHierarchy')
    position = models.ManyToManyField(HierarchyPosition, through='UserHierarchyPosition')
    representative = models.CharField(max_length=10, choices=REPRESENTATIVE, verbose_name=_('user.representative'), null=True, blank=True)
    tags = ArrayField(models.CharField(max_length=200), null=True, blank=True)
    notes = models.ManyToManyField(Note, through='UserNote')
    # UUID of batch user upload process
    process_id = models.UUIDField(null=True, blank=True)
    history = HistoricalRecords(table_name='h_user')

    def get_full_name(self):
        return f"{self.first_name or ''} {self.last_name or ''}"

    def __str__(self):
        if self.is_company:
            return self.company_name or self.get_full_name()
        return self.get_full_name()

    def get_compact_address(self):
        if self.company_address:
            return self.company_address.get_compact_address()
        elif self.home_address:
            return self.home_address.get_compact_address()
        else:
            return ''

    @staticmethod
    def get_system_user():
        return User.objects.get(status='SYSTEM')

    class Meta:
        db_table = 'user'
        verbose_name = _('Użytkownik')
        verbose_name_plural = _('Użytkownicy')
        default_permissions = ('add', 'change')
        permissions = (
            ('list_user', _('permissions.app.user.list_user')),
            ('view_user', _('permissions.app.user.view_user')),
            ('activate_user', _('permissions.app.user.activate_user')),
            ('changepassword_user', _('permissions.app.user.changepassword_user')),
            ('resetpassword_user', _('permissions.app.user.resetpassword_user')),
            ('viewinitialpassword_user', _('permissions.app.user.viewinitialpassword_user')),
            ('add_groupuser', _('permissions.app.user.add_groupuser')),
            ('change_groupuser', _('permissions.app.user.change_groupuser')),
            ('activate_groupuser', _('permissions.app.user.activate_groupuser')),
            ('list_groupuser', _('permissions.app.user.list_groupuser')),
            ('anonimize', _('permissions.app.user.anonimize')),
        )


class UserGroups(Group):
    history = HistoricalRecords(table_name='h_user_groups')


class UserHierarchy(models.Model):
    user = models.ForeignKey(User, db_column='id_user', related_name='user', on_delete=models.CASCADE)
    hierarchy = models.ForeignKey(Hierarchy, db_column='id_hierarchy', related_name='hierarchy', on_delete=models.CASCADE)

    class Meta:
        db_table = 'user_hierarchy'


class UserHierarchyPosition(models.Model):
    user = models.ForeignKey(User, db_column='id_user', related_name='position_set', on_delete=models.CASCADE)
    position = models.ForeignKey(HierarchyPosition, db_column='id_position', on_delete=models.CASCADE)

    class Meta:
        db_table = 'user_hierarchy_position'


class UserAttachment(models.Model):
    document = models.ForeignKey(User, db_column='id_document', related_name='attachment_set', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', db_column='id_parent', on_delete=models.CASCADE, null=True)
    attachment = models.ForeignKey(Attachment, db_column='id_attachment', on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200, null=True)
    is_dir = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, db_column='id_created_by', on_delete=models.PROTECT)

    class Meta:
        db_table = 'user_attachment'


class UserRelationType(models.Model):
    left_name = models.CharField(max_length=300)
    right_name = models.CharField(max_length=300)
    is_direction = models.BooleanField(default=False)

    def __str__(self):
        return self.right_name

    class Meta:
        db_table = 'user_relation_type'


class UserRelation(models.Model):
    type = models.ForeignKey(UserRelationType, verbose_name=_('user.relation.type'), db_column='id_type', on_delete=models.CASCADE)
    left = models.ForeignKey(User, verbose_name=_('user.relation.left'), db_column='id_user_left', on_delete=models.CASCADE, related_name='user_left_set')
    right = models.ForeignKey(User, verbose_name=_('user.relation.right'), db_column='id_user_right', on_delete=models.CASCADE, related_name='user_right_set')
    description = models.TextField(verbose_name=_('user.relation.description'), null=True, blank=True)
    history = HistoricalRecords(table_name='h_user_relation')

    class Meta:
        unique_together = ('left', 'right', 'type')
        db_table = 'user_relation'


class UserBatchUploadBuffer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    process_id = models.UUIDField()
    first_name = models.CharField(max_length=300, null=True, blank=True)
    last_name = models.CharField(max_length=300, null=True, blank=True)
    company_name = models.CharField(max_length=300, null=True, blank=True)
    tags = models.CharField(max_length=300, null=True, blank=True)
    phone_one = models.CharField(max_length=300, null=True, blank=True)
    email = models.CharField(max_length=300, null=True, blank=True)
    adviser_email = models.CharField(max_length=300, null=True, blank=True)
    broker_email = models.CharField(max_length=300, null=True, blank=True)
    adviser = models.IntegerField(null=True, blank=True)
    broker = models.IntegerField(null=True, blank=True)
    personal_id = models.CharField(max_length=30, null=True, blank=True)
    nip = models.CharField(max_length=30, null=True, blank=True)
    regon = models.CharField(max_length=30, null=True, blank=True)
    krs = models.CharField(max_length=30, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    street = models.CharField(max_length=200, null=True, blank=True)
    street_no = models.CharField(max_length=50, null=True, blank=True)
    apartment_no = models.CharField(max_length=50, null=True, blank=True)
    post_code = models.CharField(max_length=300, null=True, blank=True)
    errors = JSONField(default=list)
    sq = models.IntegerField()

    class Meta:
        db_table = 'user_batch_upload_buffer'


class UserBatchUploadLog(models.Model):
    id = models.UUIDField(primary_key=True)
    created_by = models.CharField(max_length=300)
    creation_date = models.DateTimeField(auto_now_add=True)
    row_count = models.IntegerField(null=True)

    class Meta:
        db_table = 'user_batch_upload_log'


class UserNote(models.Model):
    user = models.ForeignKey(User, db_column='id_user', related_name='note_set', on_delete=models.CASCADE)
    note = models.ForeignKey('note.Note', db_column='id_note', on_delete=models.CASCADE)

    class Meta:
        db_table = 'user_note'
        ordering = ['user', '-note__creation_date']
